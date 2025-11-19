# 📄 Document Indexing Pipeline

This project implements a complete document-to-vector pipeline, including text extraction, chunking, embeddings generation, and storage in PostgreSQL.
The script processes PDF/DOCX files, splits their text into chunks using a chosen strategy, generates embeddings with Google Gemini API, and stores everything in a vector-enabled PostgreSQL table.

## ✅ Project Requirements Checklist

This script fulfills all the mandatory technical requirements specified for the indexing task:

| Requirement | Implementation Status | Notes |
| :--- | :--- | :--- |
| **1. Indexing Script** (`index_documents.py`) | **Implemented** | Main execution file. |
| **Input Format** (PDF/DOCX) | **Fulfilled** | Uses Docling to support both formats. |
| **Chunking Strategy** (Fixed-size with overlap) | **Fulfilled** | Implemented via the `chunk_fixed_with_overlap` function. |
| **Embedding Generation** | **Fulfilled** | Uses `genai.embed_content` (`text-embedding-004`). |
| **Data Persistence** (PostgreSQL) | **Fulfilled** | Uses `psycopg2` and `pgvector` for storage. |
| **2. DB Schema** | **Fulfilled** | `setup_database` ensures the required table structure exists. |
| **4. Security** (`.env` file) | **Fulfilled** | API keys and DB URL are loaded securely from `.env`. |

---

## 🚀 Key Technologies

* **Language:** Python
* **Vector Model:** Google Gemini (`text-embedding-004`)
* **Document Parsing:** **Docling** (for high-quality text extraction and layout understanding)
* **Database:** PostgreSQL
* **Vector Extension:** `pgvector`

## ⚙️ Prerequisites

You must have the following items configured locally:

1.  **Python 3.8+**
2.  A **Google Gemini API Key**.
3.  **PostgreSQL Server** with the **`pgvector`** extension enabled.

## 🛠️ Installation

1.  **Clone the Repository:**
    ```bash
    git clone [YOUR-REPO-URL-HERE]
    cd [your-project-directory]
    ```

2.  **Create Virtual Environment and Install Dependencies:**
    ```bash
    python -m venv venv
    source .venv/bin/activate        # Mac/Linux
    .\.venv\Scripts\activate         # Windows
    pip install -r requirements.txt
    ```

3.  **Create a .env file:**

    Create a file named **`.env`** in the root directory to store credentials securely:
    ```env
    GEMINI_API_KEY="your_api_key_here"
    POSTGRES_URL="postgresql://user:password@localhost:5432/dbname"
    ```

    
4.  **RUN:**
    ```bash
    python index_documents.py
    ```


    You will be prompted for a file path:

    Document Indexer (Gemini + Docling + PostgreSQL)
    Enter path to PDF/DOCX file:

    example: C:\Users\Admin\Desktop\text.pdf

    You may test your pipeline with this sample PDF: "https://arxiv.org/pdf/2510.16549"
