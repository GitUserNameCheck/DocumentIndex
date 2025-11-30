from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import config

qdrant_client = QdrantClient(
    url=config.qdrant_url, 
    api_key=config.qdrant_api_key
)

collection_name = "DocumentEmbedding"

if not qdrant_client.collection_exists(collection_name=collection_name):
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=512,
            distance=models.Distance.COSINE
        ),
        hnsw_config=models.HnswConfigDiff(
            payload_m=16,
            m=0,
        ),
    )

    #might be useful later if slow
    #https://qdrant.tech/documentation/guides/multitenancy/#configure-multitenancy
    qdrant_client.create_payload_index(
        collection_name=collection_name,
        field_name="user_id",
        field_schema=models.KeywordIndexParams(
            type=models.KeywordIndexType.KEYWORD,
            is_tenant=True,
        ),
    )   

    qdrant_client.create_payload_index(
        collection_name=collection_name,
        field_name="document_id",
        field_schema=models.PayloadSchemaType.INTEGER
    )