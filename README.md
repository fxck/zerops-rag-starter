# RAG Starter for Zerops

A production-ready RAG (Retrieval-Augmented Generation) infrastructure starter that demonstrates how to build and deploy AI/LLM applications on Zerops. This is a complete working example with all the services you need for a RAG application, but with simplified implementations to keep it approachable.

[![Deploy to Zerops](https://github.com/zeropsio/recipe-shared-assets/blob/main/deploy-button/green/deploy-button.svg)](https://app.zerops.io/recipe/rag-starter)

## Architecture

This system demonstrates a complete document processing and search pipeline:

- **API Service**: FastAPI with endpoints for upload, search, status, and document listing
- **Document Processor**: Background worker that processes uploaded documents and creates embeddings
- **Dashboard**: Simple web interface built with Alpine.js
- **Vector Database**: Qdrant for storing document embeddings
- **Message Queue**: NATS for asynchronous document processing
- **Cache**: Valkey/Redis for search result caching
- **Database**: PostgreSQL for document metadata
- **Storage**: S3-compatible object storage for documents

## Services

| Service | Purpose | Technology |
|---------|---------|------------|
| api | REST API endpoints | FastAPI + Python 3.11 |
| processor | Document processing worker | Python 3.11 + SentenceTransformers |
| dashboard | Web UI | Static HTML + Alpine.js |
| db | Document metadata | PostgreSQL 16 |
| cache | Search result caching | Valkey 7.2 |
| queue | Message processing | NATS 2 |
| qdrant | Vector search | Qdrant 1.12 |
| storage | Document storage | Object Storage |

## Features

- ✅ Document upload (PDF/TXT)
- ✅ Automatic text extraction and embedding
- ✅ Vector-based document search
- ✅ Real-time status monitoring
- ✅ Document processing queue
- ✅ Search result caching
- ✅ Service health checks

## Quick Start

### One-Click Deploy

Click the deploy button above to automatically create a new Zerops project with all required services and deploy this application.

### Manual Deployment

1. Fork this repository
2. In Zerops, import `zerops-import.yml` to create the project and services
3. Connect your GitHub repository for automatic deployments
4. Or use Zerops CLI: `zcli push`

## Usage

### Upload Document

```bash
curl -X POST "http://api:8000/upload" \
  -F "file=@document.pdf"
```

### Search Documents

```bash
curl "http://api:8000/search?query=carbon+emissions"
```

### Check Status

```bash
curl "http://api:8000/status"
```

## Environment Variables

All environment variables are automatically provided by Zerops:

- Database connection: `${db_host}`, `${db_user}`, `${db_password}`
- Object storage: `${storage_accessKeyId}`, `${storage_secretAccessKey}`
- Service hostnames: `${queue_hostname}`, `${cache_hostname}`
- Qdrant credentials: `${qdrant_connectionString}`, `${qdrant_apiKey}`

## Development

### Local Testing

```bash
# Install dependencies
cd api && pip install -r requirements.txt
cd processor && pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export NATS_URL=nats://localhost:4222
# ... other variables

# Run services
python api/main.py
python processor/processor.py
```

## Monitoring

- **API Health**: `GET /status`
- **Document List**: `GET /documents`
- **Service Logs**: Available in Zerops dashboard
- **Qdrant UI**: Available at Qdrant service URL

## Where to Plug In Your LLM

This starter provides the infrastructure - you bring the AI:

1. **Text Processing** (`processor/processor.py:75`): Replace basic text extraction with proper PDF parsing and chunking
2. **Query Embeddings** (`api/main.py:195`): Replace dummy vectors with actual query embeddings
3. **Response Generation**: Add an LLM endpoint to generate answers from retrieved documents
4. **Model Selection**: The processor uses `all-MiniLM-L6-v2` - swap for your preferred embedding model

## What's Included vs What You Build

**Infrastructure (Ready to Use)**:
- ✅ Scalable Python services with auto-scaling
- ✅ Vector database (Qdrant) with collections
- ✅ PostgreSQL for metadata
- ✅ Redis/Valkey for caching  
- ✅ NATS for async job processing
- ✅ S3-compatible object storage
- ✅ Health monitoring endpoints
- ✅ Internal networking & service discovery

**AI Logic (You Implement)**:
- 🔧 Your choice of embedding model
- 🔧 Document chunking strategy
- 🔧 LLM integration (OpenAI, Anthropic, Llama, etc.)
- 🔧 Advanced search & retrieval logic
- 🔧 Authentication & multi-tenancy
