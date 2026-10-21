Workshop 3 · Giving the LLM Your Data (RAG) · notebook
AI Training · Kuehne + Nagel · Devoteam

FOLDER CONTENTS
  kn_w3_rag.ipynb                        the session notebook
  helpers.py                             helper functions (imported by the notebook)
  check_embeddings.py                    the 1-minute check from the Embedding Model Installation Guide
  data/                                  example data used in the exercises (all fictitious):
    logs/          /var/log/messages of each host (40 hosts, 5 to 7 October)
    applogs/       the billing application's own log on app-prd-03
    cmdb.csv       the CMDB export (40 rows)
    runbooks/      10 Confluence-style runbook pages (HTML)
    mini_corpus.csv, w3_test_set.json   the examples from the slides (the 12 test questions and their answer key)
    prepared/      the trainer's saved files (plan B)
  The notebook writes w3_store.json (the vector store) and w3_wall.csv (the ticket wall) into data/.

WHAT YOU NEED (install before the session)
  1. Ollama or LM Studio from Workshop 2, with Ministral 3 3B (or Gemma 4 E2B)
  2. EmbeddingGemma 300M (Embedding Model Installation Guide):
       Ollama:    ollama pull embeddinggemma
       LM Studio: google/embedding-gemma-300m (not EmbeddingGemma 2)
  3. Python 3.11 or later in a virtual environment, as in Workshop 2, with:
       pip install jupyter requests pandas numpy scikit-learn matplotlib langchain-core langchain-text-splitters fastembed
  4. The reranker model (80 MB) is downloaded by fastembed the first time section 9 runs:
     run the pre-flight cell in section 0 with internet access before the session.
     If the notebook still says a module is missing, run its first cell
     (%pip install ...) and then Kernel → Restart.

HOW TO OPEN IT
  No new environment is needed: use the one from Workshop 2.
  Open the notebook with Jupyter or VS Code and choose the kernel "Python (kn-training)"
  (Kernel → Change kernel), the one registered in the Workshop 2 Notebook Setup Guide.
  From a terminal in this folder, if the W2 and W3 folders sit side by side (macOS / Linux):
    "../K + N - W2 - Notebook/.venv/bin/jupyter" notebook kn_w3_rag.ipynb
  (Windows: "..\K + N - W2 - Notebook\.venv\Scripts\jupyter" notebook kn_w3_rag.ipynb)
  Run the install cell, then the setup cell: the notebook finds the chat model and
  EmbeddingGemma by itself, on Ollama or LM Studio (they can be on different ones).
  Run the check cell (section 0): it should print READY.

  LM Studio: start the local server (Developer tab → Start Server, port 1234).
  Ollama: the app only needs to be open (port 11434).

PRIVACY
  The notebook only talks to the local servers on your laptop. No request leaves the machine.
