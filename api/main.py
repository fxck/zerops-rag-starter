from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import httpx
import nats
import boto3
import redis
import uuid
import json
import os
from datetime import datetime

app = FastAPI(title="ESG RAG Hello World")

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service connections
s3 = None
nc = None
db_pool = None
redis_client = None

@app.on_event("startup")
async def startup():
    global nc, db_pool, s3, redis_client

    # NATS connection (no auth needed)
    nc = await nats.connect(os.getenv("NATS_URL"))

    # PostgreSQL connection
    db_pool = await asyncpg.create_pool(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    # S3 client
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv("AWS_ENDPOINT"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        use_ssl=True,
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    # Redis client (no auth needed)
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=6379,
        decode_responses=True
    )

    # Initialize database schema
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY,
                filename VARCHAR(255),
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                text_preview TEXT
            )
        """)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Generate unique ID
    doc_id = str(uuid.uuid4())

    # Save to S3
    s3.put_object(
        Bucket=os.getenv("AWS_BUCKET"),
        Key=f"documents/{doc_id}.pdf",
        Body=await file.read()
    )

    # Save metadata to PostgreSQL
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO documents (id, filename)
            VALUES ($1, $2)
        """, doc_id, file.filename)

    # Queue for processing
    await nc.publish("document.process", json.dumps({
        "id": doc_id,
        "filename": file.filename
    }).encode())

    return {"id": doc_id, "status": "queued"}

@app.get("/search")
async def search(query: str):
    # Check cache first
    cache_key = f"search:{query}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Call Qdrant for vector search
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{os.getenv('QDRANT_URL')}/collections/documents/points/search",
            headers={
                "api-key": os.getenv("QDRANT_API_KEY")
            },
            json={
                "vector": [0.1] * 384,  # Dummy vector for demo
                "limit": 3,
                "with_payload": True
            }
        )

    result = {
        "query": query,
        "results": response.json().get("result", [])
    }

    # Cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(result))

    return result

@app.get("/documents")
async def list_documents():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, filename, upload_date, processed
            FROM documents
            ORDER BY upload_date DESC
            LIMIT 10
        """)

    return [dict(row) for row in rows]

@app.get("/status")
async def status():
    services = {}

    # Check NATS
    services['nats'] = 'connected' if nc and nc.is_connected else 'disconnected'

    # Check PostgreSQL
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        services['postgresql'] = 'healthy'
    except:
        services['postgresql'] = 'unhealthy'

    # Check Qdrant
    try:
        async with httpx.AsyncClient() as client:
            await client.get(
                f"{os.getenv('QDRANT_URL')}/health",
                headers={"api-key": os.getenv("QDRANT_API_KEY")},
                timeout=2
            )
        services['qdrant'] = 'healthy'
    except:
        services['qdrant'] = 'unhealthy'

    # Check S3
    try:
        s3.list_buckets()
        services['storage'] = 'healthy'
    except:
        services['storage'] = 'unhealthy'

    # Check Redis
    try:
        redis_client.ping()
        services['cache'] = 'healthy'
    except:
        services['cache'] = 'unhealthy'

    return {"status": "operational", "services": services}