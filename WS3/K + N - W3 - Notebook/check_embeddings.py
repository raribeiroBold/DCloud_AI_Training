"""Workshop 3 · check that the local embedding model answers (Kuehne + Nagel · Devoteam).

Save it in your Workshop 2 notebook folder (the one with .venv) and run it from there:
    macOS / Linux:  .venv/bin/python check_embeddings.py
    Windows:        .venv\\Scripts\\python check_embeddings.py

Everything runs locally: the script only talks to Ollama or LM Studio on this laptop.
"""
import math
import sys

import requests

SERVERS = {"ollama": "http://localhost:11434", "lmstudio": "http://localhost:1234"}

# EmbeddingGemma expects a short instruction in front of the text (see the model card)
QUERY = "task: search result | query: {}"
DOCUMENT = "title: none | text: {}"


def list_models(runtime, url):
    try:
        if runtime == "ollama":
            return [m["name"] for m in requests.get(f"{url}/api/tags", timeout=3).json().get("models", [])]
        return [m["id"] for m in requests.get(f"{url}/v1/models", timeout=3).json().get("data", [])]
    except (requests.RequestException, ValueError):
        return None


def normalised(name):
    return name.lower().replace("-", "").replace("_", "").replace(" ", "")


def is_embeddinggemma(name):
    """EmbeddingGemma 300M, the model of the training (not EmbeddingGemma 2)."""
    n = normalised(name)
    return "embeddinggemma" in n and "embeddinggemma2" not in n


def is_embeddinggemma_2(name):
    return "embeddinggemma2" in normalised(name)


def embed(runtime, url, model, texts):
    if runtime == "ollama":
        r = requests.post(f"{url}/api/embed", json={"model": model, "input": texts}, timeout=120)
        r.raise_for_status()
        return r.json()["embeddings"]
    r = requests.post(f"{url}/v1/embeddings", json={"model": model, "input": texts}, timeout=120)
    r.raise_for_status()
    return [item["embedding"] for item in r.json()["data"]]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def main():
    found = {}
    for runtime, url in SERVERS.items():
        models = list_models(runtime, url)
        if models is None:
            print(f"  {runtime}: not running")
            continue
        match = next((m for m in models if is_embeddinggemma(m)), None)
        print(f"  {runtime}: running · embedding model: {match or 'NOT FOUND'}")
        if not match and any(is_embeddinggemma_2(m) for m in models):
            print(f"  {runtime}: EmbeddingGemma 2 found, but the training uses EmbeddingGemma 300M:"
                  " download it as well (guide, section 3.1)")
        if match:
            found[runtime] = (url, match)

    if not found:
        print("\nNOT READY. Install EmbeddingGemma (Workshop 3 guide, section 2 or 3) and start the runtime.")
        sys.exit(1)

    runtime, (url, model) = next(iter(found.items()))
    query = QUERY.format("which servers have a full disk?")
    docs = [DOCUMENT.format(t) for t in (
        "postgres[7712]: PANIC: could not write to file: No space left on device",
        "sshd[2210]: Accepted publickey for user deploy from 10.0.4.12",
    )]
    try:
        vectors = embed(runtime, url, model, [query] + docs)
    except requests.RequestException as error:
        print(f"\nNOT READY. {runtime} did not return embeddings: {error}")
        if runtime == "lmstudio":
            print("In LM Studio: Developer tab → Start server; check that the model is downloaded (lms ls).")
        sys.exit(1)

    print(f"\nUsing {runtime} · {model} · {len(vectors[0])} dimensions")
    print(f"  similarity to the disk-full log line: {cosine(vectors[0], vectors[1]):.2f}")
    print(f"  similarity to the SSH login line:     {cosine(vectors[0], vectors[2]):.2f}")
    if cosine(vectors[0], vectors[1]) > cosine(vectors[0], vectors[2]):
        print("\nREADY. The question is closer to the disk-full line, with no word in common with it.")
    else:
        print("\nThe model answers, but the result is unexpected. Tell the trainer before the session.")


if __name__ == "__main__":
    main()
