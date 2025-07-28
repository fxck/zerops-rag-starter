import asyncio
import asyncpg
import nats
import json
import boto3
import httpx
import os
from sentence_transformers import SentenceTransformer

# Initialize services
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("AWS_ENDPOINT"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    use_ssl=True,
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast model

async def process_document(msg):
    data = json.loads(msg.data.decode())
    doc_id = data['id']

    print(f"Processing document {doc_id}")

    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        # Download from S3
        obj = s3.get_object(
            Bucket=os.getenv("AWS_BUCKET"),
            Key=f"documents/{doc_id}.pdf"
        )
        content = obj['Body'].read()

        # Extract text (simplified - just use first 500 chars for demo)
        text = content.decode('utf-8', errors='ignore')[:500]

        # Create embedding
        embedding = model.encode(text).tolist()

        # Store in Qdrant
        async with httpx.AsyncClient() as client:
            await client.put(
                f"{os.getenv('QDRANT_URL')}/collections/documents/points",
                headers={
                    "api-key": os.getenv("QDRANT_API_KEY")
                },
                json={
                    "points": [{
                        "id": doc_id,
                        "vector": embedding,
                        "payload": {
                            "text": text,
                            "filename": data['filename'],
                            "doc_id": doc_id
                        }
                    }]
                }
            )

        # Update PostgreSQL
        await conn.execute("""
            UPDATE documents
            SET processed = true, text_preview = $1
            WHERE id = $2
        """, text[:200], doc_id)

        print(f"Processed document {doc_id}")

    finally:
        await conn.close()

async def main():
    nc = await nats.connect(os.getenv("NATS_URL"))

    # Subscribe to processing queue
    sub = await nc.subscribe("document.process", cb=process_document)

    print("Processor started, waiting for documents...")

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())