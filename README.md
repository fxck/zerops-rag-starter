# ESG Legal Compliance RAG - Hello World

A minimal demonstration of an ESG Legal Compliance RAG (Retrieval-Augmented Generation) system deployed on Zerops infrastructure.

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

## Deployment

### Prerequisites

1. Zerops account with sufficient credits
2. Project configured with the required services

### Step 1: Create Services

Create the following services in Zerops:

```yaml
services:
  - hostname: db
    type: postgresql@16
    mode: NON_HA
  - hostname: cache
    type: valkey@7.2
    mode: NON_HA
  - hostname: queue
    type: nats@2
    mode: NON_HA
  - hostname: qdrant
    type: qdrant@1.12
    mode: NON_HA
  - hostname: storage
    type: object-storage
    objectStorageSize: 2
    objectStoragePolicy: public-read
```

### Step 2: Deploy Application

```bash
# From project root
zcli push
```

### Step 3: Verify Deployment

1. Check service status at the dashboard
2. Upload a test document
3. Perform a search query

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

## Limitations

This is a "Hello World" implementation with the following limitations:

- No authentication/authorization
- Basic text extraction (first 500 chars)
- Dummy embeddings for search queries in demo mode
- Limited error handling
- Single-tenant design
