from sentence_transformers import SentenceTransformer

# Load once (important for performance)
model = SentenceTransformer("bert-base-nli-mean-tokens")

def get_embedding(text):
    return model.encode(text)
