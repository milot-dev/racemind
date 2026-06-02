from pathlib import Path
from functools import lru_cache
import os
import re
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

MODEL_NAME = "all-MiniLM-L6-v2"


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 80) -> list[str]:
    text = text.strip()

    if not text:
        return []

    sections = re.split(r"(?=^##\s+)", text, flags=re.MULTILINE)

    chunks = []

    for section in sections:
        section = clean_text(section)

        if not section:
            continue

        if len(section) <= chunk_size:
            chunks.append(section)
            continue

        start = 0
        while start < len(section):
            end = start + chunk_size
            chunk = section[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

    return chunks

def load_knowledge_base() -> list[dict[str, str]]:
    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        return documents

    for path in KNOWLEDGE_BASE_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        chunks = chunk_text(content)

        for index, chunk in enumerate(chunks):
            documents.append(
                {
                    "source": path.name,
                    "chunk_id": f"{path.name}-{index}",
                    "text": chunk,
                }
            )

    return documents


@lru_cache(maxsize=1)
def load_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def build_vector_index() -> dict[str, Any]:
    documents = load_knowledge_base()

    if not documents:
        return {
            "documents": [],
            "embeddings": np.array([]),
        }

    model = load_embedding_model()
    texts = [doc["text"] for doc in documents]
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    return {
        "documents": documents,
        "embeddings": embeddings,
    }


def retrieve_context(question: str, top_k: int = 4) -> list[dict[str, Any]]:
    index = build_vector_index()
    documents = index["documents"]
    embeddings = index["embeddings"]

    if not documents or embeddings.size == 0:
        return []

    model = load_embedding_model()
    question_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    scores = cosine_similarity(question_embedding, embeddings)[0]

    ranked_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for idx in ranked_indices:
        doc = documents[int(idx)]
        results.append(
            {
                "source": doc["source"],
                "chunk_id": doc["chunk_id"],
                "text": doc["text"],
                "score": float(scores[idx]),
            }
        )

    return results


def build_fallback_answer(question: str, retrieved_chunks: list[dict[str, Any]]) -> str:
    if not retrieved_chunks:
        return (
            "I could not find enough relevant information in the RaceMind AI "
            "knowledge base to answer this question yet."
        )

    question_lower = question.lower()
    combined_context = "\n\n".join(chunk["text"] for chunk in retrieved_chunks)

    # Split context into short sentence-like units.
    sentences = re.split(r"(?<=[.!?])\s+", combined_context)

    # Remove markdown headings and empty lines.
    cleaned_sentences = []
    for sentence in sentences:
        sentence = re.sub(r"#+\s*", "", sentence).strip()
        sentence = sentence.replace("\n", " ").strip()

        if sentence:
            cleaned_sentences.append(sentence)

    # Simple keyword scoring to choose only the most relevant sentences.
    stopwords = {
        "what", "is", "are", "the", "a", "an", "of", "in", "on", "for", "to",
        "and", "or", "with", "why", "how", "explain", "difference", "between",
        "important", "motogp", "motorcycle", "racing"
    }

    question_terms = {
        term
        for term in re.findall(r"[a-zA-Z0-9]+", question_lower)
        if term not in stopwords and len(term) > 2
    }

    scored_sentences = []

    for sentence in cleaned_sentences:
        sentence_lower = sentence.lower()
        score = sum(1 for term in question_terms if term in sentence_lower)

        if score > 0:
            scored_sentences.append((score, sentence))

    scored_sentences.sort(key=lambda item: item[0], reverse=True)

    selected_sentences = [sentence for _, sentence in scored_sentences[:3]]

    # Fallback if keyword scoring finds nothing useful.
    if not selected_sentences:
        selected_sentences = cleaned_sentences[:2]

    concise_answer = " ".join(selected_sentences)

    # Keep answer short and readable.
    if len(concise_answer) > 700:
        concise_answer = concise_answer[:700].rsplit(" ", 1)[0] + "."

    return (
        f"{concise_answer}\n\n"
        "Source: RaceMind AI knowledge base."
    )

def answer_with_openai(question: str, retrieved_chunks: list[dict[str, Any]]) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        context = "\n\n".join(
            [
                f"Source: {chunk['source']}\n{chunk['text']}"
                for chunk in retrieved_chunks
            ]
        )

        prompt = f"""
You are RaceMind AI, an expert MotoGP and motorcycle racing assistant.

Answer the user's question using the provided context.
If the context is not enough, say that the RaceMind AI knowledge base does not contain enough information yet.
Keep the answer clear, technical when useful, and beginner-friendly.

Context:
{context}

Question:
{question}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are RaceMind AI, a MotoGP and motorcycle racing assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.4,
        )

        return response.choices[0].message.content

    except Exception as exc:
        return (
            "OpenAI generation failed, so RaceMind AI used the local retrieved context instead.\n\n"
            + build_fallback_answer(question, retrieved_chunks)
            + f"\n\nInternal note: {str(exc)}"
        )


def answer_question(question: str) -> dict[str, Any]:
    retrieved_chunks = retrieve_context(question)

    openai_answer = answer_with_openai(question, retrieved_chunks)

    if openai_answer:
        answer = openai_answer
        mode = "vector_rag_openai"
    else:
        answer = build_fallback_answer(question, retrieved_chunks)
        mode = "vector_rag_local_fallback"

    sources = sorted({chunk["source"] for chunk in retrieved_chunks})

    return {
        "answer": answer,
        "sources": sources,
        "retrieval_mode": mode,
        "matches": [
            {
                "source": chunk["source"],
                "score": round(chunk["score"], 4),
            }
            for chunk in retrieved_chunks
        ],
    }