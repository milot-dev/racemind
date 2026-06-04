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

# Retrieval tuning for a small local knowledge base.
# If answers are too strict, lower MIN_VECTOR_SCORE slightly.
# If unrelated questions still get answers, raise it slightly.
MIN_VECTOR_SCORE = 0.32
MIN_KEYWORD_OVERLAP = 1
TOP_K = 4

OUT_OF_SCOPE_ANSWER = (
    "I could not find enough relevant information in the RaceMind AI "
    "knowledge base to answer this question yet."
)

STOPWORDS = {
    "what", "whats", "is", "are", "am", "was", "were", "be", "being", "been",
    "the", "a", "an", "of", "in", "on", "at", "for", "to", "from", "by", "as",
    "and", "or", "with", "without", "into", "than", "then", "that", "this", "these",
    "those", "it", "its", "they", "them", "their", "he", "she", "his", "her",
    "do", "does", "did", "can", "could", "should", "would", "will", "may", "might",
    "you", "me", "my", "your", "we", "our", "us", "i",
    "tell", "explain", "describe", "define", "meaning", "difference", "between",
    "about", "why", "how", "when", "where", "which", "who",
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_markdown(text: str) -> str:
    """Remove markdown headings/bold/list symbols from text used in final answers."""
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"^[-*]\s+", "", text, flags=re.MULTILINE)
    return clean_text(text)


def tokenize(text: str) -> set[str]:
    terms = set()

    for term in re.findall(r"[a-zA-Z0-9]+", text.lower()):
        if term in STOPWORDS or len(term) <= 2:
            continue

        # Very small normalization to match plural/singular forms.
        if len(term) > 4 and term.endswith("s"):
            term = term[:-1]

        terms.add(term)

    return terms


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[dict[str, str]]:
    """
    Split markdown by H2 sections first.
    Each chunk keeps a title separately so final answers can avoid repeating headings.
    """
    text = text.strip()

    if not text:
        return []

    h1_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    document_title = h1_match.group(1).strip() if h1_match else "Knowledge Base"

    # Remove the H1 from the body before splitting into H2 sections.
    body = re.sub(r"^#\s+.+$", "", text, count=1, flags=re.MULTILINE).strip()

    sections = re.split(r"(?=^##\s+)", body, flags=re.MULTILINE)
    chunks: list[dict[str, str]] = []

    # If the file has intro text before the first H2, keep it as a chunk.
    for section in sections:
        section = section.strip()
        if not section:
            continue

        title = document_title
        title_match = re.match(r"^##\s+(.+)$", section, flags=re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            section_body = re.sub(r"^##\s+.+$", "", section, count=1, flags=re.MULTILINE).strip()
        else:
            section_body = section

        section_body = strip_markdown(section_body)
        if not section_body:
            continue

        full_text = f"{title}. {section_body}"

        if len(full_text) <= chunk_size:
            chunks.append({"title": title, "text": full_text, "body": section_body})
            continue

        start = 0
        while start < len(section_body):
            end = start + chunk_size
            piece = section_body[start:end].strip()
            if piece:
                chunks.append({"title": title, "text": f"{title}. {piece}", "body": piece})
            start += chunk_size - overlap

    return chunks


def load_knowledge_base() -> list[dict[str, str]]:
    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        return documents

    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        chunks = chunk_text(content)

        for index, chunk in enumerate(chunks):
            documents.append(
                {
                    "source": path.name,
                    "chunk_id": f"{path.name}-{index}",
                    "title": chunk["title"],
                    "text": chunk["text"],
                    "body": chunk["body"],
                    "keywords": " ".join(sorted(tokenize(chunk["text"]))),
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


def keyword_overlap_score(question_terms: set[str], chunk_text_value: str) -> int:
    chunk_terms = tokenize(chunk_text_value)
    return len(question_terms.intersection(chunk_terms))


def retrieve_context(question: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
    question = clean_text(question)
    question_terms = tokenize(question)

    if not question or not question_terms:
        return []

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

    vector_scores = cosine_similarity(question_embedding, embeddings)[0]

    candidates = []
    for idx, doc in enumerate(documents):
        vector_score = float(vector_scores[idx])
        overlap = keyword_overlap_score(question_terms, doc["text"])

        # Boost exact title matches such as "race pace", "DNF", "tire degradation".
        title = doc.get("title", "").lower()
        title_terms = tokenize(title)
        title_overlap = len(question_terms.intersection(title_terms))

        combined_score = vector_score + (overlap * 0.05) + (title_overlap * 0.08)

        candidates.append(
            {
                "source": doc["source"],
                "chunk_id": doc["chunk_id"],
                "title": doc["title"],
                "text": doc["text"],
                "body": doc["body"],
                "score": vector_score,
                "keyword_overlap": overlap,
                "combined_score": combined_score,
            }
        )

    candidates.sort(key=lambda item: item["combined_score"], reverse=True)

    # Relevance gate: vector similarity alone is not enough, because embeddings always
    # return nearest neighbors even for unrelated questions.
    relevant = [
        item
        for item in candidates
        if item["score"] >= MIN_VECTOR_SCORE and item["keyword_overlap"] >= MIN_KEYWORD_OVERLAP
    ]

    return relevant[:top_k]


def has_enough_context(retrieved_chunks: list[dict[str, Any]]) -> bool:
    if not retrieved_chunks:
        return False

    best = retrieved_chunks[0]
    return (
        best.get("score", 0.0) >= MIN_VECTOR_SCORE
        and best.get("keyword_overlap", 0) >= MIN_KEYWORD_OVERLAP
    )


def sentence_split(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", strip_markdown(text))
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def build_fallback_answer(question: str, retrieved_chunks: list[dict[str, Any]]) -> str:
    if not has_enough_context(retrieved_chunks):
        return OUT_OF_SCOPE_ANSWER

    question_terms = tokenize(question)
    best_chunk = retrieved_chunks[0]

    scored_sentences = []
    for chunk in retrieved_chunks:
        for sentence in sentence_split(chunk.get("body") or chunk["text"]):
            sentence_terms = tokenize(sentence)
            overlap = len(question_terms.intersection(sentence_terms))
            if overlap > 0:
                scored_sentences.append((overlap, chunk["score"], sentence))

    scored_sentences.sort(key=lambda item: (item[0], item[1]), reverse=True)

    selected_sentences: list[str] = []
    seen = set()

    for _, _, sentence in scored_sentences:
        normalized = sentence.lower()
        if normalized in seen:
            continue
        selected_sentences.append(sentence)
        seen.add(normalized)
        if len(selected_sentences) >= 2:
            break

    if not selected_sentences:
        selected_sentences = sentence_split(best_chunk.get("body") or best_chunk["text"])[:2]

    concise_answer = " ".join(selected_sentences).strip()

    if len(concise_answer) > 450:
        concise_answer = concise_answer[:450].rsplit(" ", 1)[0].rstrip(".,;:") + "."

    return f"{concise_answer}\n\nSource: RaceMind AI knowledge base."


def answer_with_openai(question: str, retrieved_chunks: list[dict[str, Any]]) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or not has_enough_context(retrieved_chunks):
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        context = "\n\n".join(
            [
                f"Source: {chunk['source']}\nTitle: {chunk['title']}\nText: {chunk['body']}"
                for chunk in retrieved_chunks
            ]
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are RaceMind AI, a MotoGP and motorcycle racing assistant. "
                        "Answer only from the provided RaceMind AI knowledge base context. "
                        "If the context does not answer the question, say the knowledge base "
                        "does not contain enough information yet. Keep answers concise: 1-3 sentences. "
                        "Do not include markdown headings. Do not invent facts."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion:\n{question}",
                },
            ],
            temperature=0.2,
            max_tokens=180,
        )

        answer = response.choices[0].message.content or ""
        return strip_markdown(answer)

    except Exception:
        # Do not expose internal API errors to the frontend user.
        return None


def answer_question(question: str) -> dict[str, Any]:
    question = clean_text(question)
    retrieved_chunks = retrieve_context(question)

    if not has_enough_context(retrieved_chunks):
        return {
            "answer": OUT_OF_SCOPE_ANSWER,
            "sources": [],
            "retrieval_mode": "out_of_scope",
            "matches": [],
        }

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
                "title": chunk["title"],
                "score": round(chunk["score"], 4),
                "keyword_overlap": chunk["keyword_overlap"],
            }
            for chunk in retrieved_chunks
        ],
    }
