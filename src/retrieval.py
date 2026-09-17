import json
from pathlib import Path
import os
import numpy as np
from google import genai


KNOWLEDGE_BASE_DIR = Path("knowledge_base")
VECTOR_STORE_DIR = Path("data/vector_store")

EMBEDDING_MODEL = "gemini-embedding-001"


def load_documents() -> list[dict]:
    documents = []

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.md"):
        documents.append({
            "source": file_path.name,
            "text": file_path.read_text(encoding="utf-8")
        })

    return documents


def split_into_chunks(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100
) -> list[str]:

    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def create_chunks(documents: list[dict]) -> list[dict]:
    chunks = []

    for document in documents:
        document_chunks = split_into_chunks(document["text"])

        for chunk in document_chunks:
            chunks.append({
                "source": document["source"],
                "text": chunk
            })

    return chunks


def create_embeddings(
    chunks: list[dict],
    client: genai.Client
) -> np.ndarray:

    embeddings = []

    for chunk in chunks:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=chunk["text"]
        )

        embeddings.append(response.embeddings[0].values)

    return np.array(embeddings, dtype=np.float32)


def save_vector_store(
    chunks: list[dict],
    embeddings: np.ndarray
) -> None:

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    np.save(
        VECTOR_STORE_DIR / "embeddings.npy",
        embeddings
    )

    metadata = {
        "chunks": chunks
    }

    with open(
        VECTOR_STORE_DIR / "metadata.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2
        )


def ingest_knowledge_base() -> None:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured"
        )

    client = genai.Client(api_key=api_key)

    documents = load_documents()

    if not documents:
        raise RuntimeError(
            "No knowledge base documents found"
        )

    chunks = create_chunks(documents)

    if not chunks:
        raise RuntimeError(
            "No chunks were created from knowledge base"
        )

    embeddings = create_embeddings(
        chunks,
        client
    )

    save_vector_store(
        chunks,
        embeddings
    )

    print(f"Loaded documents: {len(documents)}")
    print(f"Created chunks: {len(chunks)}")
    print(f"Embedding shape: {embeddings.shape}")
    print("Knowledge base ingestion completed.")

def load_vector_store() -> tuple[list[dict], np.ndarray]:
    embeddings_path = VECTOR_STORE_DIR / "embeddings.npy"
    metadata_path = VECTOR_STORE_DIR / "metadata.json"

    if not embeddings_path.exists() or not metadata_path.exists():
        raise RuntimeError(
            "Vector store not found. Run ingestion first."
        )

    embeddings = np.load(embeddings_path)

    with open(
        metadata_path,
        "r",
        encoding="utf-8"
    ) as file:
        metadata = json.load(file)

    return metadata["chunks"], embeddings


def cosine_similarity(
    query_vector: np.ndarray,
    document_vectors: np.ndarray
) -> np.ndarray:

    query_norm = np.linalg.norm(query_vector)
    document_norms = np.linalg.norm(
        document_vectors,
        axis=1
    )

    if query_norm == 0:
        raise ValueError("Query embedding has zero magnitude.")

    similarities = np.dot(
        document_vectors,
        query_vector
    ) / (
        document_norms * query_norm
    )

    return similarities


def retrieve_relevant_chunks(
    query: str,
    client: genai.Client,
    top_k: int = 3
) -> list[dict]:

    chunks, embeddings = load_vector_store()

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query
    )

    query_embedding = np.array(
        response.embeddings[0].values,
        dtype=np.float32
    )

    similarities = cosine_similarity(
        query_embedding,
        embeddings
    )

    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for index in top_indices:
        results.append({
            "source": chunks[index]["source"],
            "text": chunks[index]["text"],
            "score": float(similarities[index])
        })

    return results


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    ingest_knowledge_base()