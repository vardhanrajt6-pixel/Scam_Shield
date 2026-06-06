from sentence_transformers import SentenceTransformer, util

# Load embedding model once
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    model = None

def compute_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts.
    Returns a float between -1 and 1.
    """
    if model is None:
        return 0.0

    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    return round(similarity, 4)
