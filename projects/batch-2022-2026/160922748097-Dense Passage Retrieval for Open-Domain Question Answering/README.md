# Dense Passage Retrieval for Open-Domain Question Answering

A small GUI-based demo project implementing Dense Passage Retrieval (DPR) and baseline retrieval approaches for open-domain question answering. The project provides a Tkinter GUI to upload a dataset, generate or load DPR embeddings (using SentenceTransformers), run baseline TF‑IDF + cosine retrieval, evaluate DPR and a Bi-Encoder extension, and interactively ask questions against the generated embedding index.

## Highlights

- Uses `sentence-transformers` DPR-style model (`intfloat/e5-large-v2`) for dense embeddings.
- Includes a TF‑IDF + cosine baseline for quick comparison.
- Simple Tkinter GUI for uploading dataset, generating embeddings, evaluating models and asking questions.
- Embeddings and data saved to a local `model/` folder to avoid re-computation.

## Requirements

- Python 3.8 or later (3.10/3.11 recommended)
- Windows: PowerShell is used in examples below

Recommended Python packages (see `requirements.txt`):

- sentence-transformers
- scikit-learn
- pandas
- numpy

Tkinter is part of the Python standard library for most CPython installations on Windows; if the GUI doesn't open, ensure your Python installation includes Tk support.

## Files

- `DensePassageRetrieval.py` — Main GUI application. Handles dataset upload, embedding generation, evaluation, and interactive querying.
- `model/` — Directory created at runtime to store NumPy files:
  - `X_train_dpr.npy` — DPR train question embeddings
  - `X_test_dpr.npy` — DPR test question embeddings
  - `y_train.npy` / `y_test.npy` — Corresponding answers arrays
- `README.md` — This file
- `requirements.txt` — Python dependencies (created alongside this README)

## Expected dataset format

Create a folder and place two CSV files named `train.csv` and `test.csv` with at least these columns:

- `question` — the question text (string)
- `answers` — the ground-truth answers (string or list-like representation)

Example (train.csv):

question,answers
"What is the capital of France?","Paris"

The GUI will prompt you to choose the dataset folder (the folder that contains `train.csv` and `test.csv`).

## How it works (brief)

- The app uses `SentenceTransformer("intfloat/e5-large-v2")` as the DPR model. It prefixes queries with `"query: "` before encoding to match the model usage in the script.
- Embeddings are normalized and saved to `model/` as `.npy` files to speed up subsequent runs.
- The TF‑IDF baseline uses `TfidfVectorizer(stop_words='english')` and cosine similarity.
- Accuracy evaluation is performed by checking whether any of the top-K retrieved training answers appear in the test answer (boolean match). The script uses `TOP_K = 5` and `TEST_LIMIT = 200` by default.

## Installation

Open PowerShell and run:

```powershell
# create and activate a virtual environment (optional but recommended)
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt
```

If you prefer not to use `requirements.txt`, you can install individual packages:

```powershell
pip install sentence-transformers scikit-learn pandas numpy
```

Note: The first time you run the app it will download the SentenceTransformers model(s) — this requires an internet connection and some RAM/disk space.

## Usage

1. Launch the GUI:

```powershell
python "DensePassageRetrieval.py"
```

2. Click "Upload Dataset" and select the folder containing `train.csv` and `test.csv`.
3. Click "Generate / Load Embeddings". The app will generate DPR embeddings and save them to `model/` on first run. Subsequent runs will load the saved `.npy` files.
4. Use the buttons to run the TF‑IDF baseline, DPR evaluation, or the Bi‑Encoder extension.
5. Click "Ask Question" to provide a question; the app will use the saved DPR embeddings to return the top-5 predicted answers.

## Customization

- `TOP_K` and `TEST_LIMIT` are module-level constants at the top of `DensePassageRetrieval.py`. Modify them if you want different retrieval depth or evaluation size.
- To change models, edit the `dpr_model` / `bert_model` lines near the top. Example models used in the script:
  - DPR / dense: `intfloat/e5-large-v2`
  - Bi-Encoder extension: `nli-distilroberta-base-v2`

## Troubleshooting

- If the GUI doesn't appear or raises a `tkinter` error, verify your Python installation includes Tk. On Windows, install CPython from python.org with the default installer which includes Tk by default.
- If model downloads fail, check your internet connection and firewall settings. Models can be quite large.
- If you have memory issues when encoding a large dataset, consider reducing `TEST_LIMIT` or splitting your dataset.
- If answers don't match due to casing/punctuation, the script lower-cases text during normalization; however, exact substring matching may still miss some edge cases. Consider normalizing punctuation or using fuzzy matching if you want more flexible evaluation.

## Suggested next steps

- Add a small CLI wrapper so the app can run in headless mode for batch experiments.
- Add unit tests for the retrieval functions and normalization logic.
- Add a simple example dataset and a short demo script that runs end-to-end and prints results.
- Add a `LICENSE` and `CONTRIBUTING.md` for collaboration.

## Credits

Built using the SentenceTransformers library and scikit-learn for baselines. GUI built with Tkinter.

---

If you'd like, I can also:

- add a small example dataset (train/test CSV) to the repo,
- add a CLI runner script,
- or open a PR that adds unit tests for evaluation and retrieval.

Tell me which of those you'd like next.