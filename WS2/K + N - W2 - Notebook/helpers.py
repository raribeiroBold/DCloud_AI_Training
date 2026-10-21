"""Session helpers for the Workshop 2 notebook (Kuehne + Nagel · Devoteam).

Only what is specific to the session lives here: a small client for the local LLM
(Ollama or LM Studio), JSON checks, masking of personal data and the plot style.
Data handling, metrics and plots are done in the notebook with pandas, scikit-learn
and matplotlib.

Everything runs locally: no request leaves the machine.
"""
import json
import random
import re
import time

import matplotlib.pyplot as plt
import requests

CONFIG = {"runtime": None, "model": None, "base_url": None}

DEFAULT_URL = {"ollama": "http://localhost:11434", "lmstudio": "http://localhost:1234"}
PREFERRED = ("ministral", "gemma")   # models used in the training, in order of preference

# Devoteam palette
PALETTE = {"red": "#F8485E", "grey": "#3C3C3A", "muted": "#7A7A7A", "teal": "#94D1D1", "green": "#5AB891",
           "blue": "#4A8CCA", "pink": "#FDDADE", "mint": "#D7EBE7", "sand": "#E9DCC9"}


class ServerError(Exception):
    """The local server rejected the request (for example, a prompt larger than the context window)."""


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
# Local LLM: configuration
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


def _usable(name):
    n = name.lower()
    return "embed" not in n and "cloud" not in n


def configure(runtime=None, model=None, base_url=None):
    """Choose the runtime ("ollama" or "lmstudio") and the model.

    With no arguments: use whichever local server is running and has a Ministral or Gemma model.
    """
    found = {}
    for rt in ([runtime] if runtime else ["ollama", "lmstudio"]):
        if rt not in DEFAULT_URL:
            raise ValueError('runtime must be "ollama" or "lmstudio"')
        url = base_url or DEFAULT_URL[rt]
        models = _list_models(rt, url)
        if models is not None:
            found[rt] = (url, [m for m in models if _usable(m)])

    choice = None
    for rt, (url, models) in found.items():
        if model:
            if model in models:
                choice = (rt, url, model)
                break
            continue
        for keyword in PREFERRED:
            match = next((m for m in models if keyword in m.lower()), None)
            if match:
                choice = (rt, url, match)
                break
        if choice:
            break

    if choice is None:
        CONFIG.update(runtime=None, model=None, base_url=None)
        lines = ["No usable local model found."]
        lines += [f"  {rt} is running at {url} with: {', '.join(m) or 'no models'}" for rt, (url, m) in found.items()]
        lines += [f"  {rt} is not running." for rt in DEFAULT_URL if rt not in found]
        lines += ["Fix one of these, then run this cell again:",
                  "  Ollama:    ollama pull ministral-3:3b",
                  "  LM Studio: download mistralai/ministral-3-3b, load it and start the server (Developer tab)"]
        raise RuntimeError("\n".join(lines))
    CONFIG.update(runtime=choice[0], base_url=choice[1], model=choice[2])
    print(f"Using {choice[0]} at {choice[1]} · model: {choice[2]}")


def show_models():
    """List the installed models and flag models that run in the cloud."""
    for name in _list_models(CONFIG["runtime"], CONFIG["base_url"]) or []:
        flag = "  ← WARNING: runs in the cloud, data leaves the machine" if "cloud" in name.lower() else ""
        in_use = "  ← in use" if name == CONFIG["model"] else ""
        print(f"  {name}{in_use}{flag}")


# ---------------------------------------------------------------------------
# Local LLM: calls
# ---------------------------------------------------------------------------

def _messages(prompt, system=None):
    msgs = [{"role": "system", "content": system}] if system else []
    return msgs + [{"role": "user", "content": prompt}]


def chat(prompt, system=None, temperature=0.0, max_tokens=200, seed=None, num_ctx=None, schema=None):
    """Send one request to the local model.

    Returns a dict with: text, prompt_tokens, response_tokens, total_seconds and, on Ollama,
    prompt_seconds, prompt_tok_s and response_tok_s.
    schema: a JSON schema that forces the answer into that format.
    num_ctx: context window size (Ollama only; in LM Studio it is set when the model is loaded).
    """
    if not CONFIG["model"]:
        raise RuntimeError("No model configured: run configure() in section 0.")
    start = time.perf_counter()
    if CONFIG["runtime"] == "ollama":
        options = {"temperature": temperature, "num_predict": max_tokens}
        if seed is not None:
            options["seed"] = seed
        if num_ctx is not None:
            options["num_ctx"] = num_ctx
        body = {"model": CONFIG["model"], "messages": _messages(prompt, system), "stream": False, "options": options}
        if schema is not None:
            body["format"] = schema
        r = requests.post(f"{CONFIG['base_url']}/api/chat", json=body, timeout=600)
        if r.status_code >= 400:
            raise ServerError(f"{r.status_code}: {r.text[:300]}")
        d = r.json()
        result = {"text": d.get("message", {}).get("content", ""),
                  "prompt_tokens": d.get("prompt_eval_count", 0), "response_tokens": d.get("eval_count", 0),
                  "prompt_seconds": d.get("prompt_eval_duration", 0) / 1e9}
        response_seconds = d.get("eval_duration", 0) / 1e9
        result["prompt_tok_s"] = result["prompt_tokens"] / result["prompt_seconds"] if result["prompt_seconds"] else None
        result["response_tok_s"] = result["response_tokens"] / response_seconds if response_seconds else None
    else:
        body = {"model": CONFIG["model"], "messages": _messages(prompt, system), "temperature": temperature,
                "max_tokens": max_tokens, "stream": False}
        if seed is not None:
            body["seed"] = seed
        if schema is not None:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "answer", "strict": True, "schema": schema}}
        r = requests.post(f"{CONFIG['base_url']}/v1/chat/completions", json=body, timeout=600)
        if r.status_code >= 400:
            raise ServerError(f"{r.status_code}: {r.text[:300]}")
        d = r.json()
        usage = d.get("usage", {})
        result = {"text": d["choices"][0]["message"].get("content") or "",
                  "prompt_tokens": usage.get("prompt_tokens", 0), "response_tokens": usage.get("completion_tokens", 0),
                  "prompt_seconds": None, "prompt_tok_s": None, "response_tok_s": None}
    result["total_seconds"] = time.perf_counter() - start
    return result


def ask(prompt, **options):
    """Shortcut: only the text of the answer."""
    return chat(prompt, **options)["text"].strip()


def ask_many(prompt, n=10, **options):
    """The same request n times: a list of answers."""
    return [ask(prompt, **options) for _ in range(n)]


def measure_speed(prompt, max_tokens=60, num_ctx=None):
    """Prompt reading (prefill) vs generation (decode) speed for one request.

    Ollama reports both timings; for LM Studio the time to first token is measured while streaming.
    num_ctx: Ollama only (in LM Studio the window is set when the model is loaded).
    """
    if CONFIG["runtime"] == "ollama":
        r = chat(prompt, max_tokens=max_tokens, num_ctx=num_ctx)
        return {"prompt_tokens": r["prompt_tokens"], "prompt_seconds": r["prompt_seconds"],
                "prompt_tok_s": r["prompt_tok_s"], "response_tok_s": r["response_tok_s"]}
    body = {"model": CONFIG["model"], "messages": _messages(prompt), "temperature": 0, "max_tokens": max_tokens,
            "stream": True, "stream_options": {"include_usage": True}}
    start, first, chunks, usage = time.perf_counter(), None, 0, {}
    with requests.post(f"{CONFIG['base_url']}/v1/chat/completions", json=body, stream=True, timeout=600) as r:
        if r.status_code >= 400:
            raise ServerError(f"{r.status_code}: {r.text[:300]}")
        for line in r.iter_lines():
            if not line.startswith(b"data: ") or line == b"data: [DONE]":
                continue
            d = json.loads(line[6:])
            usage = d.get("usage") or usage
            choices = d.get("choices") or []
            if choices and choices[0].get("delta", {}).get("content"):
                chunks += 1
                first = first or time.perf_counter()
    end = time.perf_counter()
    prompt_seconds = (first or end) - start
    response_seconds = end - (first or end)
    prompt_tokens = usage.get("prompt_tokens")
    return {"prompt_tokens": prompt_tokens, "prompt_seconds": prompt_seconds,
            "prompt_tok_s": prompt_tokens / prompt_seconds if prompt_tokens and prompt_seconds else None,
            "response_tok_s": usage.get("completion_tokens", chunks) / response_seconds if response_seconds else None}


_TOKEN_BASELINE = {}


def count_tokens(text):
    """Approximate number of tokens the local model uses for a text.

    Measures the prompt with and without the text; each request starts with a different
    marker so the server does not reuse cached computations.
    """
    def prompt_tokens(t):
        return chat(f"#{random.randint(10000, 99999)}\n{t}", max_tokens=1)["prompt_tokens"]
    key = (CONFIG["runtime"], CONFIG["model"])
    if key not in _TOKEN_BASELINE:
        _TOKEN_BASELINE[key] = prompt_tokens("")
    return max(prompt_tokens(text) - _TOKEN_BASELINE[key], 0)


# ---------------------------------------------------------------------------
# Answers: cleaning and JSON checks
# ---------------------------------------------------------------------------

def clean(text):
    """Strip markdown formatting (bold, code) from a short answer."""
    return re.sub(r"[*`_#]", "", text).strip()


def valid_json(text, fields=None):
    """Is the answer pure JSON, as a script would read it with json.loads? Returns (valid, reason, object)."""
    t = text.strip()
    try:
        obj = json.loads(t)
    except json.JSONDecodeError:
        if t.startswith("```"):
            return False, "JSON inside a code block", None
        return (False, "text around the JSON", None) if "{" in t else (False, "not JSON", None)
    if fields:
        if not isinstance(obj, dict):
            return False, "JSON without the requested fields", obj
        missing = [f for f in fields if f not in obj]
        extra = [f for f in obj if f not in fields]
        if missing or extra:
            return False, f"missing: {missing} · extra: {extra}", obj
    return True, "valid", obj


def extract_json(text):
    """Salvage the JSON from a "dirty" answer (code block, text around it), as a script would have to."""
    t = re.sub(r"```(?:json)?", "", text)
    start, end = t.find("{"), t.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(t[start:end + 1])
    except json.JSONDecodeError:
        return None


def usable_json(text, fields):
    """True if, after cleaning, the JSON has exactly the requested fields, as text (not lists)."""
    obj = extract_json(text)
    return isinstance(obj, dict) and sorted(obj) == sorted(fields) and all(isinstance(v, str) for v in obj.values())


# ---------------------------------------------------------------------------
# Personal data
# ---------------------------------------------------------------------------

IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
USER_PATTERN = re.compile(r"(?i)\b(user[= ]|for (?:invalid user )?|uid=)([A-Za-z0-9._-]+)")


def mask(text):
    """Replace IP addresses, emails and usernames with placeholders."""
    text = EMAIL_PATTERN.sub("[EMAIL]", text)
    text = IP_PATTERN.sub("[IP]", text)
    return USER_PATTERN.sub(lambda m: m.group(1) + "[USER]", text)


def find_identifiers(text):
    """IP addresses and emails still present in a text."""
    return IP_PATTERN.findall(text) + EMAIL_PATTERN.findall(text)

