from sentence_transformers import SentenceTransformer
import torch
from app.core.config import config

embedding_model = SentenceTransformer(config.embedding_model_path)

if torch.cuda.is_available():
    embedding_model = embedding_model.to('cuda')
