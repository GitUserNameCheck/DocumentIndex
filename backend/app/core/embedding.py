from sentence_transformers import SentenceTransformer
import torch
from app.core.config import config

model = SentenceTransformer(config.embedding_model_path)

if torch.cuda.is_available():
    model = model.to('cuda')
