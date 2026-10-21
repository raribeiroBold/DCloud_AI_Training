"""Session helpers for the Workshop 3 notebook (Kuehne + Nagel · Devoteam).

Only what is specific to the session lives here: a small client for the local models
(Ollama or LM Studio, chat and embeddings), a reader for the runbook pages and the plot style.
Parsing, chunking, BM25, fusion and the metrics are written in the notebook itself, so you can read every step.
The LangChain pieces that only connect our local models live here: an Embeddings class over EmbeddingGemma
and a model step for chains (it works the same on Ollama and LM Studio).

Everything runs locally: no request leaves the machine.
"""
import re
import time
from html.parser import HTMLParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import requests
from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableLambda

CONFIG = {"runtime": None, "model": None, "base_url": None}            # chat model (W2)
EMBEDDER = {"runtime": None, "model": None, "base_url": None}          # embedding model (W3)

DEFAULT_URL = {"ollama": "http://localhost:11434", "lmstudio": "http://localhost:1234"}
PREFERRED = ("ministral", "gemma")   # chat models of the training, in order of preference

# EmbeddingGemma expects a short instruction in front of the text (model card)
QUERY_PREFIX = "task: search result | query: "
DOCUMENT_PREFIX = "title: none | text: "

# Devoteam palette
PALETTE = {"red": "#F8485E", "grey": "#3C3C3A", "muted": "#7A7A7A", "teal": "#94D1D1", "green": "#5AB891",
           "blue": "#4A8CCA", "pink": "#FDDADE", "mint": "#D7EBE7", "sand": "#E9DCC9"}


class ServerError(Exception):
    """The local server rejected the request."""


# ---------------------------------------------------------------------------
# Plot style
# ---------------------------------------------------------------------------

def set_style():
    """Brand colours and a clean look for every matplotlib / pandas plot."""
    plt.rcParams.update({
        "axes.prop_cycle": plt.cycler(color=[PALETTE[c] for c in ("blue", "red", "teal", "green", "sand", "grey")]),
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": PALETTE["muted"],
        "axes.titleweight": "bold", "axes.titlesize": 11, "figure.dpi": 110,
        "axes.labelcolor": PALETTE["grey"], "xtick.color": PALETTE["grey"], "ytick.color": PALETTE["grey"],
        "text.color": PALETTE["grey"], "legend.frameon": False,
    })


# ---------------------------------------------------------------------------
# Local models: configuration
# ---------------------------------------------------------------------------

def _list_models(runtime, base_url):
    """Models available on one runtime, or None if its server is not running."""
    try:
        if runtime == "ollama":
            r = requests.get(f"{base_url}/api/tags", timeout=3)
            return [m["name"] for m in r.json().get("models", [])]
        r = requests.get(f"{base_url}/v1/models", timeout=3)
        return [m["id"] for m in r.json().get("data", [])]
    except (requests.RequestException, ValueError):
        return None


def _normalised(name):
    return name.lower().replace("-", "").replace("_", "").replace(" ", "")


def _is_embedder(name):
    """EmbeddingGemma 300M, the embedding model of the training (not EmbeddingGemma 2)."""
    n = _normalised(name)
    return "embeddinggemma" in n and "embeddinggemma2" not in n


def _is_chat(name):
    n = name.lower()
    return "embed" not in n and "cloud" not in n


def configure(runtime=None, model=None, embed_runtime=None, embed_model=None):
    """Find the chat model (W2) and the embedding model (W3) on Ollama or LM Studio.

    With no arguments: use whichever local server has them. The two can be on different
    runtimes (for example the chat model in LM Studio and EmbeddingGemma in Ollama).
    """
    found = {rt: _list_models(rt, url) for rt, url in DEFAULT_URL.items()}
    running = {rt: models for rt, models in found.items() if models is not None}

    # chat model
    chat_choice = None
    for rt, models in running.items():
        if runtime and rt != runtime:
            continue
        usable = [m for m in models if _is_chat(m)]
        pick = model if model in usable else next((m for k in PREFERRED for m in usable if k in m.lower()), None)
        if pick:
            chat_choice = (rt, pick)
            break
    if chat_choice:
        CONFIG.update(runtime=chat_choice[0], model=chat_choice[1], base_url=DEFAULT_URL[chat_choice[0]])
        print(f"Chat model:      {chat_choice[1]} on {chat_choice[0]}")
    else:
        CONFIG.update(runtime=None, model=None, base_url=None)
        print("Chat model:      NOT FOUND (only section 1 needs it): install Ministral 3 3B as in Workshop 2")

    # embedding model
    emb_choice = None
    for rt, models in running.items():
        if embed_runtime and rt != embed_runtime:
            continue
        pick = embed_model if embed_model in models else next((m for m in models if _is_embedder(m)), None)
        if pick:
            emb_choice = (rt, pick)
            break
    if emb_choice:
        EMBEDDER.update(runtime=emb_choice[0], model=emb_choice[1], base_url=DEFAULT_URL[emb_choice[0]])
        print(f"Embedding model: {emb_choice[1]} on {emb_choice[0]}")
    else:
        EMBEDDER.update(runtime=None, model=None, base_url=None)
        has_v2 = any("embeddinggemma2" in _normalised(m) for models in running.values() for m in models)
        lines = ["Embedding model: NOT FOUND."]
        if has_v2:
            lines.append("  EmbeddingGemma 2 is installed, but the training uses EmbeddingGemma 300M: download it as well.")
        lines += [f"  {rt} is not running." for rt in DEFAULT_URL if rt not in running]
        lines += ["Fix one of these, then run this cell again:",
                  "  Ollama:    ollama pull embeddinggemma",
                  "  LM Studio: lms get google/embedding-gemma-300m, and start the server (Developer tab)"]
        raise RuntimeError("\n".join(lines))


def show_models():
    """List the installed models on every running runtime and flag models that run in the cloud."""
    for rt, url in DEFAULT_URL.items():
        models = _list_models(rt, url)
        if models is None:
            continue
        print(f"{rt}:")
        for name in models:
            flag = "  ← WARNING: runs in the cloud, data leaves the machine" if "cloud" in name.lower() else ""
            used = "  ← chat" if (rt, name) == (CONFIG["runtime"], CONFIG["model"]) else ""
            used += "  ← embeddings" if (rt, name) == (EMBEDDER["runtime"], EMBEDDER["model"]) else ""
            print(f"  {name}{used}{flag}")


# ---------------------------------------------------------------------------
# Local models: calls
# ---------------------------------------------------------------------------

def chat(prompt, system=None, temperature=0.0, max_tokens=200):
    """Send one request to the local chat model. Returns a dict with text and total_seconds."""
    if not CONFIG["model"]:
        raise RuntimeError("No chat model configured: run configure() in section 0.")
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    start = time.perf_counter()
    if CONFIG["runtime"] == "ollama":
        body = {"model": CONFIG["model"], "messages": messages, "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens}}
        r = requests.post(f"{CONFIG['base_url']}/api/chat", json=body, timeout=600)
        if r.status_code >= 400:
            raise ServerError(f"{r.status_code}: {r.text[:300]}")
        text = r.json().get("message", {}).get("content") or ""
    else:
        body = {"model": CONFIG["model"], "messages": messages, "temperature": temperature,
                "max_tokens": max_tokens, "stream": False}
        r = requests.post(f"{CONFIG['base_url']}/v1/chat/completions", json=body, timeout=600)
        if r.status_code >= 400:
            raise ServerError(f"{r.status_code}: {r.text[:300]}")
        text = r.json()["choices"][0]["message"].get("content") or ""
    return {"text": text, "total_seconds": time.perf_counter() - start}


def ask(prompt, **options):
    """Shortcut: only the text of the answer."""
    return chat(prompt, **options)["text"].strip()


_CACHE = {}


def embed(texts, role="document", batch=32):
    """Turn texts into vectors with EmbeddingGemma: one row of 768 numbers per text.

    role="query" adds the query prefix ("task: search result | query: "), role="document"
    the document prefix ("title: none | text: "), as the model card asks.
    Vectors already computed in this session are reused (the cache), so a second call is instant.
    """
    if not EMBEDDER["model"]:
        raise RuntimeError("No embedding model configured: run configure() in section 0.")
    if isinstance(texts, str):
        texts = [texts]
    prefix = QUERY_PREFIX if role == "query" else DOCUMENT_PREFIX
    inputs = [prefix + str(t) for t in texts]
    todo = [t for t in dict.fromkeys(inputs) if (EMBEDDER["model"], t) not in _CACHE]
    for i in range(0, len(todo), batch):
        part = todo[i:i + batch]
        if EMBEDDER["runtime"] == "ollama":
            r = requests.post(f"{EMBEDDER['base_url']}/api/embed", json={"model": EMBEDDER["model"], "input": part}, timeout=600)
            if r.status_code >= 400:
                raise ServerError(f"{r.status_code}: {r.text[:300]}")
            vectors = r.json()["embeddings"]
        else:
            r = requests.post(f"{EMBEDDER['base_url']}/v1/embeddings", json={"model": EMBEDDER["model"], "input": part}, timeout=600)
            if r.status_code >= 400:
                raise ServerError(f"{r.status_code}: {r.text[:300]}")
            vectors = [item["embedding"] for item in sorted(r.json()["data"], key=lambda d: d["index"])]
        for t, v in zip(part, vectors):
            _CACHE[(EMBEDDER["model"], t)] = np.asarray(v, dtype=np.float32)
    return np.vstack([_CACHE[(EMBEDDER["model"], t)] for t in inputs])


def cosine(a, b):
    """Cosine similarity between two vectors: 1 = same direction, 0 = unrelated."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ---------------------------------------------------------------------------
# Runbook pages (Confluence-style HTML export)
# ---------------------------------------------------------------------------

class _PageReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta, self.title, self.sections = {}, "", []
        self._in, self._text = None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and "name" in a:
            self.meta[a["name"]] = a.get("content", "")
        elif tag in ("h1", "h2"):
            self._flush()
            self._in = tag
        elif tag == "li":
            self._text.append("\n- ")

    def handle_endtag(self, tag):
        if tag == "h1":
            self.title, self._text, self._in = "".join(self._text).strip(), [], None
        elif tag == "h2":
            self.sections.append(["".join(self._text).strip(), ""])
            self._text, self._in = [], None
        elif tag in ("p", "ol", "ul"):
            self._text.append("\n")

    def handle_data(self, data):
        self._text.append(data)

    def _flush(self):
        if self.sections and self._in is None:
            self.sections[-1][1] += "".join(self._text)
        self._text = []

    def close(self):
        super().close()
        self._flush()


def read_runbook(path):
    """Parse one runbook page: page id, title, owner team, last update and its sections (heading, text)."""
    reader = _PageReader()
    reader.feed(Path(path).read_text(encoding="utf-8"))
    reader.close()
    sections = []
    for heading, text in reader.sections:
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
        sections.append((heading, "\n".join(line for line in lines if line)))
    return {"page": reader.meta.get("page-id", Path(path).stem), "title": reader.title,
            "owner_team": reader.meta.get("owner"), "last_updated": reader.meta.get("last-updated"),
            "sections": sections}


# ---------------------------------------------------------------------------
# LangChain connectors for the local models
# ---------------------------------------------------------------------------

class GemmaEmbeddings(Embeddings):
    """LangChain Embeddings over EmbeddingGemma: document prefix for chunks, query prefix for questions."""

    def embed_documents(self, texts):
        return embed(list(texts), role="document").tolist()

    def embed_query(self, text):
        return embed(text, role="query")[0].tolist()


def local_llm(max_tokens=300, temperature=0.0):
    """A chain step that sends a prompt to the local chat model and returns its text."""
    def call(prompt):
        text = prompt.to_string() if hasattr(prompt, "to_string") else str(prompt)
        return ask(text, max_tokens=max_tokens, temperature=temperature)
    return RunnableLambda(call)
