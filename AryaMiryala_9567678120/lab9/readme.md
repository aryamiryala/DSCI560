# Open-Source RAG Pipeline with Streamlit

## Overview

This project implements a fully local, open-source Retrieval-Augmented Generation (RAG) pipeline. It allows users to upload PDF documents (such as the ADS Cookbook and licensing guides) and chat with them using a locally hosted LLM. This completely replaces the original skeleton code's reliance on closed-source, paid OpenAI APIs.

---

## Key Features

- **Local PDF Extraction:** Processes multiple PDFs and safely extracts text.
- **Optimized Chunking (Section 2b):** Uses `CharacterTextSplitter` with a strict `chunk_size=500` and `chunk_overlap=100` to maintain contextual integrity.
- **Open-Source Vector Store (Section 2c & 3):** Replaces OpenAI embeddings with `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace, stored in a local **FAISS** database.
- **Local LLM (Section 3):** Utilizes `LlamaCpp` to run a quantized Llama-2 model (`llama-2-7b-chat.Q2_K.gguf`) entirely offline.
- **Contextual Memory (Section 2d):** Implements `ConversationBufferMemory` from LangChain to allow for multi-turn, context-aware conversations.
- **Driver Logic (Section 2e):** Includes a specific termination command — type `exit` to gracefully end the session.

---

## Important Environment Notes (Apple Silicon / Mac Users)

Building `faiss-cpu` from source via pip frequently fails on newer macOS versions (M1/M2/M3) and Python 3.12 due to missing C++ headers and NumPy 2.x incompatibilities.

If you are running this on a Mac, **Python 3.11 is highly recommended**, and you must follow the Conda installation steps below to ensure the FAISS vector database compiles correctly.

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/aryamiryala/DSCI560.git
cd lab9
```

### 2. Create and activate a virtual environment (Python 3.11)
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install FAISS via Conda (Mac Users Only)

If you are on an M-series Mac, bypass pip for FAISS and use Conda to grab the pre-compiled binaries:
```bash
conda install -c pytorch faiss-cpu
```

> **Note:** You may need to symbolically link the Conda FAISS installation to your venv's `site-packages` depending on your local paths.

### 4. Install required Python packages
```bash
pip install -r requirements.txt
```

> **Note:** `numpy<2` is strictly required in `requirements.txt`, as the FAISS binaries are currently incompatible with NumPy 2.x.

---

## Usage

1. Start the Streamlit application:
```bash
    streamlit run app.py
```

2. Open your browser to `http://localhost:8501`.

3. In the left sidebar, upload your PDF documents (e.g., `Ads cookbook.pdf`).

4. Click the **Process** button and wait for the terminal to finish generating the vector embeddings.

5. Use the chat interface to ask questions about your documents.

6. Type `exit` in the chat box to terminate the session.