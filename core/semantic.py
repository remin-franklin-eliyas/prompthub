import numpy as np
from sentence_transformers import SentenceTransformer
from models.schemas import Version

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embedding(text: str) -> bytes:
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tobytes()


def load_embedding(data: bytes) -> np.ndarray:
    return np.frombuffer(data, dtype=np.float32)


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    if norm == 0:
        return 0.0
    similarity = dot / norm
    return round(1 - float(similarity), 4)


def describe_distance(distance: float) -> str:
    if distance < 0.1:
        return "near identical"
    elif distance < 0.25:
        return "minor change"
    elif distance < 0.45:
        return "moderate change"
    elif distance < 0.65:
        return "significant change"
    else:
        return "major rewrite"


def detect_structural_changes(old: str, new: str) -> list[dict]:
    changes = []

    old_lines = set(old.strip().splitlines())
    new_lines = set(new.strip().splitlines())

    added = new_lines - old_lines
    removed = old_lines - new_lines

    keywords = {
        "format": ["json", "bullet", "numbered", "markdown", "table", "format"],
        "length": ["concise", "brief", "detailed", "short", "long", "words", "sentences"],
        "tone": ["formal", "casual", "professional", "friendly", "conversational", "expert"],
        "reasoning": ["step by step", "chain of thought", "think through", "reason", "explain"],
        "role": ["you are", "act as", "your role", "as an", "as a"],
    }

    for category, words in keywords.items():
        in_old = any(w in old.lower() for w in words)
        in_new = any(w in new.lower() for w in words)

        if in_new and not in_old:
            changes.append({"type": "added", "category": category})
        elif in_old and not in_new:
            changes.append({"type": "removed", "category": category})

    old_len = len(old)
    new_len = len(new)
    delta = new_len - old_len
    if abs(delta) > 20:
        direction = "longer" if delta > 0 else "shorter"
        changes.append({
            "type": "modified",
            "category": "length",
            "detail": f"{abs(delta)} chars {direction}"
        })

    return changes


def diff_versions(v1: Version, v2: Version) -> dict:
    if v1.embedding and v2.embedding:
        e1 = load_embedding(v1.embedding)
        e2 = load_embedding(v2.embedding)
        distance = cosine_distance(e1, e2)
    else:
        distance = None

    structural = detect_structural_changes(v1.content, v2.content)

    return {
        "v1_tag": v1.version_tag,
        "v2_tag": v2.version_tag,
        "distance": distance,
        "description": describe_distance(distance) if distance is not None else "no embeddings",
        "structural_changes": structural,
        "v1_chars": len(v1.content),
        "v2_chars": len(v2.content),
        "char_delta": len(v2.content) - len(v1.content),
    }