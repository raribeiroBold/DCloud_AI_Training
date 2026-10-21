Workshop 2 · How LLMs Work · notebook
AI Training · Kuehne + Nagel · Devoteam

FOLDER CONTENTS
  kn_w2_how_llms_work.ipynb   the session notebook
  helpers.py                  helper functions (imported by the notebook)
  data/                       example logs, alerts and tickets (all fictitious)

WHAT YOU NEED (install before the session, see the two setup guides)
  1. Ollama or LM Studio, with Ministral 3 3B and/or Gemma 4 E2B
     (Local Model Installation Guide)
  2. Python 3.11 or later, in a virtual environment (Notebook Setup Guide)
  3. Jupyter (or VS Code with the Jupyter extension) and the libraries:
       pip install jupyter requests pandas scikit-learn matplotlib
     If the notebook still says a module is missing, run its first cell
     (%pip install ...) and then Kernel → Restart.

HOW TO OPEN IT
  In the notebook folder:  jupyter notebook kn_w2_how_llms_work.ipynb
  Run the install cell, then the setup cell: the notebook finds Ollama or LM Studio
  and the installed model by itself.
  Run the check cell (section 0): it should answer "ready".

  LM Studio: start the local server (Developer tab → Start Server, port 1234).
  Ollama: the app only needs to be open (port 11434).

PRIVACY
  The notebook only talks to the local server on your laptop. No request leaves the machine.
