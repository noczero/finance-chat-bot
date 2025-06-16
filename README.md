# RAG-based Financial Statement Q&A System

A full-stack application that uses RAG (Retrieval Augmented Generation) technology to answer questions about financial statements. 
The system uses OpenAI's GPT model for text generation and ChromaDB for vector storage.


https://github.com/user-attachments/assets/364bebc8-cfba-4b00-ab09-c2a254451a08


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

# API Specification

It's available on http://localhost:8000/docs
<img width="1912" alt="Screenshot 2025-06-17 at 00 33 11" src="https://github.com/user-attachments/assets/87280bce-ff7c-4e81-89f1-3a5e8f51e7df" />

## Endpoints

The API endpoints are grouped by functionality: Chats, Documents, and Conversations.

### **Chats**

This section covers the endpoint for interacting with the AI.

#### POST `/api/chat`

Processes a chat request and returns an AI-generated response based on the uploaded documents.

* **Description**: Send a question to the AI. You can optionally include a `conversation_token` to continue an existing conversation.
* **Request Body**: `application/json`
    ```json
    {
      "conversation_token": "string" (optional),
      "question": "string" (required)
    }
    ```
* **Responses**:
    * `200 OK`: Successful response. The structure of the success response is not detailed in the schema.
    * `422 Unprocessable Entity`: The request was well-formed but could not be processed due to validation errors.

---

### **Documents**

These endpoints are used for managing the lifecycle of documents within the system.

#### POST `/api/upload`

Uploads and processes a new PDF file.

* **Description**: This endpoint accepts a PDF file, processes it, and makes it available for the Q&A system.
* **Request Body**: `multipart/form-data`
    * `file`: The PDF file (`.pdf`) to be uploaded.
* **Responses**:
    * `200 OK`: The file was uploaded and processed successfully.
    * `422 Unprocessable Entity`: Validation error, likely due to an incorrect file format or a missing file.

#### GET `/api/documents`

Retrieves a list of all processed documents.

* **Description**: Fetches metadata or a list of documents that have been successfully uploaded and processed.
* **Responses**:
    * `200 OK`: Returns a list of documents. The exact structure is not defined.

#### DELETE `/api/documents`

Clears all documents and associated data from the system.

* **Description**: This is a destructive operation that removes all uploaded files and deletes the corresponding vector store data.
* **Responses**:
    * `200 OK`: All documents and data have been successfully cleared.

#### GET `/api/documents/chunks`

Retrieves document chunks with pagination.

* **Description**: Useful for debugging or understanding how a document was divided into smaller pieces for processing by the RAG system.
* **Query Parameters**:
    * `limit` (integer, optional, default: 100): The maximum number of chunks to return. Maximum value is 1000.
    * `offset` (integer, optional, default: 0): The starting point from which to return chunks.
* **Responses**:
    * `200 OK`: Returns a paginated list of document chunks.
    * `422 Unprocessable Entity`: Invalid query parameter values.

---

### **Conversations**

Endpoints for managing conversation history.

#### GET `/api/conversations`

Retrieves a list of all conversations.

* **Description**: Each conversation is a sequence of questions and answers identified by a unique token.
* **Responses**:
    * `200 OK`: Returns a list of conversations.

#### GET `/api/conversations/{token}/messages`

Retrieves all messages for a specific conversation.

* **Description**: Fetches the history of a single conversation using its unique token.
* **Path Parameters**:
    * `token` (string, required): The unique identifier for the conversation.
* **Responses**:
    * `200 OK`: Returns a list of messages for the specified conversation.
    * `422 Unprocessable Entity`: The provided token is invalid or does not exist.

---

### **System**

#### GET `/`

A health check endpoint for the service.

* **Description**: Can be used to verify that the API is running and available.
* **Responses**:
    * `200 OK`: The service is healthy.

***

## Schemas

These are the data models used in the API requests and responses.

### `ChatRequest`

Used for the body of the `POST /api/chat` request.

| Field                | Type          | Description                                         |
| -------------------- | ------------- | --------------------------------------------------- |
| `conversation_token` | string / null | Optional token to continue an existing conversation. |
| `question`           | string        | The question to ask the AI.                         |

### `HTTPValidationError`

The standard error response format for validation errors (`422`).

| Field    | Type    | Description                                 |
| -------- | ------- | ------------------------------------------- |
| `detail` | array   | An array of `ValidationError` objects.      |

### `ValidationError`

Details a specific validation failure.

| Field | Type               | Description                                |
| ----- | ------------------ | ------------------------------------------ |
| `loc` | array[string/int]  | The location of the error (e.g., in the request body, a specific field). |
| `msg` | string             | A human-readable message describing the error. |
| `type`| string             | The type of error (e.g., 'value_error.missing'). |
