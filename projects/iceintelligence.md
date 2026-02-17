---
layout: default
title: IceIntelligence
parent: Security & Malware Analysis
nav_order: 10
---

# IceIntelligence

[View on GitHub](https://github.com/icepaule/IceIntelligence){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }

***

## Project Overview

IceIntelligence is a powerful, self-hosted AI orchestration platform designed to enhance your productivity and insights, especially in sensitive domains like cybersecurity and financial document management. Built with a focus on data privacy and local processing, it leverages Large Language Models (LLMs) via Ollama, integrates with your personal documents (RAG), performs controlled internet research, and automates document classification and tagging with Paperless-NGX.

**Key Principles:**
-   **Local-First Processing:** All sensitive data and LLM inferences remain within your local network.
-   **Security by Design:** Strict adherence to data privacy, with no external cloud API dependencies for core intelligence.
-   **Modular and Extensible:** A flexible architecture allowing easy integration of new tools and capabilities.

## Features

-   **LLM Orchestration (Ollama):** Utilizes local Ollama instances for various LLM tasks, supporting multiple models.
-   **Retrieval-Augmented Generation (RAG):** Integrates with your private document collection (e.g., cybersecurity reports, forensic analyses) to provide expert knowledge. This system ensures that the LLM's answers are grounded in your specific data, without needing to retrain the model.
-   **Secure Internet Research:** Performs controlled web searches and extracts relevant text content, feeding it to the LLM for analysis without direct internet exposure for the LLM itself.
-   **Paperless-NGX Integration:** Automates the classification, titling, and tagging of documents within your Paperless-NGX instance using LLM intelligence, enhancing your document management workflow.
-   **Parallel Task Execution:** Designed to handle multiple AI-driven tasks concurrently or in the background.

## Setup Instructions

### Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Ollama:**
    *   Install Ollama from [ollama.com](https://ollama.com/).
    *   Ensure the Ollama server is running.
    *   Download the recommended models:
        ```bash
        ollama run llama3.1:8b # For general LLM tasks
        ollama run nomic-embed-text # For document embeddings (RAG)
        ```
    *   If you prefer different models, update the `.env` file accordingly.

2.  **Python 3.10+:**
    ```bash
    sudo apt update
    sudo apt install python3.12 python3.12-venv python3-pip
    ```

3.  **Git:**
    ```bash
    sudo apt install git
    ```

4.  **Paperless-NGX Instance:** A running instance of Paperless-NGX with API access enabled. You will need an API token.

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/IceIntelligence.git
    cd IceIntelligence
    ```
    *(Note: The repository is currently private. Adjust the cloning command once the actual GitHub repository is created.)*

2.  **Create and Activate a Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables (`.env` file):**
    Copy the example environment file and fill in your specific details:
    ```bash
    cp .env.example .env
    ```
    Now, edit the newly created `.env` file:
    ```bash
    nano .env # or your preferred text editor
    ```
    Ensure the following variables are set:

    ```ini
    # .env - Environment variables for IceIntelligence

    # Ollama Configuration
    OLLAMA_HOST=http://localhost:11434 # Or your Ollama server's address
    OLLAMA_LLM_MODEL=llama3.1:8b # Your preferred LLM model for general tasks
    OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest # Your preferred embedding model for RAG

    # Paperless-NGX Configuration
    PAPERLESS_URL=http://192.168.178.108:8010 # Your Paperless-NGX instance URL
    PAPERLESS_API_TOKEN=YOUR_PAPERLESS_API_TOKEN # <<< CRITICAL: REPLACE WITH YOUR ACTUAL PAPERLESS API TOKEN >>>

    # Worker ID (optional, will be generated if not provided)
    # WORKER_ID=my-ollama-worker
    ```
    **SECURITY WARNING:** Never commit your `.env` file with actual secrets to version control. The `.gitignore` file is configured to prevent this.

5.  **Prepare RAG Documents:**
    Place your private documents (e.g., `.txt`, `.pdf`) into the `data/` directory:
    ```bash
    mkdir data # If it doesn't exist
    # Copy your documents here, e.g.:
    cp /path/to/your/cybersecurity_reports/*.pdf data/
    cp /path/to/your/forensic_notes/*.txt data/
    ```

## Running the Application

To start the FastAPI server:

```bash
cd IceIntelligence
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The `--reload` flag is useful for development as it automatically restarts the server on code changes. For production, remove `--reload`.

Access the API documentation at `http://localhost:8000/docs` in your web browser.

## Usage

Interact with the API using the `/docs` endpoint for a user-friendly interface or directly via `curl` or `requests`.

### Example Tasks:

1.  **Index Documents for RAG:**
    This task loads documents from the `data/` directory, chunks them, and stores their embeddings in the local ChromaDB. This is crucial for the RAG system to access your private knowledge.
    *   **Endpoint:** `POST /tasks/`
    *   **Body:**
        ```json
        {
          "name": "index_documents",
          "description": "Initial indexing of local documents."
        }
        ```
    *   **Wait for completion:** You might need to check the task status or logs for completion.

2.  **Perform Research (Internet & RAG):**
    Submits a research query. The system will perform an internet search, retrieve relevant content, and combine it with your local RAG documents to formulate an answer using the LLM.
    *   **Endpoint:** `POST /tasks/`
    *   **Body:**
        ```json
        {
          "name": "research",
          "description": "What are the latest zero-day vulnerabilities affecting industrial control systems?"
        }
        ```

3.  **Classify and Tag Paperless-NGX Document:**
    Provides a document ID from your Paperless-NGX instance. The LLM will analyze its content and suggest a title, document type, and tags, which are then updated in Paperless-NGX.
    *   **Endpoint:** `POST /tasks/`
    *   **Body:**
        ```json
        {
          "name": "classify_paperless_document",
          "description": "123" # Replace '123' with the actual document ID from Paperless-NGX
        }
        ```
    *   **Important:** Ensure your `PAPERLESS_API_TOKEN` is correctly set in `.env` and has sufficient permissions.

## Security Considerations

-   **No External LLM Calls:** This setup is designed to use *only* your local Ollama instance. No data leaves your network for LLM processing.
-   **Controlled Internet Access:** The `InternetSearch` module is explicitly designed to retrieve text content. The LLM itself does not directly browse the web.
-   **API Tokens:** Protect your `PAPERLESS_API_TOKEN`. Never hardcode it or commit it to version control. Use the `.env` file as instructed.
-   **Network Segmentation:** For production environments, consider isolating the IceIntelligence server within your network to further restrict access.

## Future Enhancements

-   **Enhanced Task Management:** More sophisticated task queuing, prioritization, and error handling.
-   **More LLM Tools:** Integration with other specialized tools for code analysis, vulnerability scanning, etc.
-   **Advanced UI:** A custom web interface for easier interaction and visualization.
-   **Dynamic Ollama Model Management:** API endpoints to list, pull, and manage Ollama models dynamically.
-   **User Authentication/Authorization:** For multi-user environments.
-   **Document Upload to Paperless-NGX:** Directly upload files to Paperless-NGX through the API.
