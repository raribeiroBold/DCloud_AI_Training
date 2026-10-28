"""Build the Chroma collection for the W4 Part 1 RAG demo (slide 78).

Loads the W3 runbooks (one chunk per <h2> section, with page-id, title and owner
as metadata) into a persistent Chroma collection, using Chroma's default local
embedding model (all-MiniLM-L6-v2, ONNX): nothing leaves the laptop.

Run with the same chromadb that chroma-mcp uses, so the on-disk format matches.
From the WS4 folder (the script finds its files from its own location, so any folder works
as long as the path to the script is right):
    uv run --python 3.12 --no-project --with chroma-mcp python rag/build_chroma.py
"""
from html.parser import HTMLParser
from pathlib import Path

import chromadb

HERE = Path(__file__).resolve().parent
RUNBOOKS = HERE.parent / "runbooks"  # WS4/runbooks
DB_DIR = HERE / "chroma_db"
COLLECTION = "runbooks"


class Runbook(HTMLParser):
    """Collects meta tags, the <h1> title and the text of each <h2> section."""

    def __init__(self):
        super().__init__()
        self.meta, self.title, self.sections = {}, "", []
        self._tag = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and "name" in attrs:
            self.meta[attrs["name"]] = attrs.get("content", "")
        if tag == "h2":
            self.sections.append(["", ""])
        self._tag = tag

    def handle_endtag(self, tag):
        self._tag = None

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self._tag == "h1":
            self.title = text
        elif self._tag == "h2":
            self.sections[-1][0] = text
        elif self.sections:
            self.sections[-1][1] += (" " if self.sections[-1][1] else "") + text
        else:  # text before the first <h2>
            self.sections.append(["Overview", text])


def chunks():
    for path in sorted(RUNBOOKS.glob("RB-*.html")):
        rb = Runbook()
        rb.feed(path.read_text(encoding="utf-8"))
        page_id = rb.meta.get("page-id", path.stem)
        for n, (heading, body) in enumerate(rb.sections, start=1):
            yield {
                "id": f"{page_id}-{n}",
                # short header in the text, as in W3: title > section, then the body
                "document": f"{rb.title} > {heading}\n{body}",
                "metadata": {
                    "page_id": page_id,
                    "title": rb.title,
                    "section": heading,
                    "owner": rb.meta.get("owner", ""),
                    "last_updated": rb.meta.get("last-updated", ""),
                },
            }


def main():
    items = list(chunks())
    if not items:
        raise SystemExit(f"No RB-*.html files in {RUNBOOKS}: run this from the WS4 folder copy.")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    col = client.create_collection(COLLECTION)  # default local embedding model
    col.add(
        ids=[i["id"] for i in items],
        documents=[i["document"] for i in items],
        metadatas=[i["metadata"] for i in items],
    )
    print(f"{col.count()} chunks from {len({i['metadata']['page_id'] for i in items})} runbooks in {DB_DIR}")

    question = "What is our runbook for a PostgreSQL volume above 90%?"
    hits = col.query(query_texts=[question], n_results=3)
    print(f"\nCheck: {question}")
    for doc_id, dist in zip(hits["ids"][0], hits["distances"][0]):
        print(f"  {doc_id}  distance {dist:.3f}")


if __name__ == "__main__":
    main()
