# Question Paper OBE Agent - Full Lab 1-10 Implementation

## Project Overview
A comprehensive Agentic AI system built progressively from Lab 1 to Lab 10, culminating in a multi-agent Question Paper Generation and OBE Analysis System. 

This system uses real data (21 scanned university PDFs extracted via Tesseract OCR) to generate compliant question papers, map CO/PO, and analyze Bloom's Taxonomy.

## OBE Pipeline Enhancements

The paper-generation workflow includes dedicated blueprint, question-selection,
Bloom/CO-PO tagging, and difficulty/coverage analysis agents. The coordinator
stores its coverage analysis in each generated paper, and the dashboard includes
estimated difficulty in the Coverage & Quality report.

Semantic retrieval uses a local Chroma database with deterministic local
embeddings. It does not send question-bank content to an embedding service.
Install the optional components with:

```bash
python -m pip install -r requirements-ai.txt
```

Vector retrieval is enabled by default and can be disabled with
`ENABLE_VECTOR_RETRIEVAL=0`.

Question tagging uses rules by default. To enable Gemini tagging, set
`GEMINI_API_KEY` in the environment (do not commit the key). `GEMINI_MODEL`
optionally selects a model; the default is `gemini-2.5-flash`. When Gemini is
enabled, question text is sent to Google's Gemini API for classification.
Without the key, all tagging remains local.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub and create a Streamlit Community Cloud app
   using `app.py` as the entry point.
2. In the app's **Settings → Secrets**, configure an initial administrator:

   ```toml
   [initial_admin]
   id = "your-admin-id"
   password = "choose-a-strong-password"
   ```

   Keep these values private. The app creates this administrator if the ID
   does not already exist; it does not overwrite existing accounts. You can
   also add `GEMINI_API_KEY` here to enable Gemini tagging; it is optional.
3. The root `requirements.txt` and `packages.txt` install the Python
   dependencies and Linux Tesseract OCR needed by the app.

The faculty database and generated documents are stored on the app's local
filesystem. Streamlit Community Cloud does not guarantee that local files
survive restarts, so this setup is suitable for a demo, not durable production
storage. For long-term use, move account data to a managed database and
generated files to persistent object storage.

## How to Run the Full Demonstration
Run the master script from the root directory:
```bash
python main.py