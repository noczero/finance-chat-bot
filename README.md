# RAG-based Financial Statement Q&A System

A full-stack application that uses RAG (Retrieval Augmented Generation) technology to answer questions about financial statements. 
The system uses OpenAI's GPT model for text generation and ChromaDB for vector storage.

## Features
- Clean web interface with Next.js
- FastAPI backend with async support
- Q&A using OpenAI's GPT model
- Source citation in answers
- Support Chat History and context continuity
- Multiple PDF document uploading and ingestion
- Document chunking and embedding
- Vector-based semantic search using ChromaDB


## Tech Stack

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- LangChain
- OpenAI API
- ChromaDB
- pdfplumber
- SQLite
- SQLAlchemy

## Prerequisites

- Python 3.13.5+
- Node.js 20.17.0+
- OpenAI API key
- npm or yarn

## Setup

### Backend Setup

1. Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```
Fill the `.env` with your configuration.

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

## Usage

1. Start the services using script.
```bash
./scripts/run_services.sh
```
2. Open the web application in your browser: http://localhost:3000.
3. Upload a document PDF file.
4. Wait for the document to be processed.
5. Start asking questions about the document.
6. View the AI-generated answers with source citations.
7. Ask more about new questions or start another conversation.