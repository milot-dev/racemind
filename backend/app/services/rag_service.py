from pathlib import Path
from functools import lru_cache
from collections import Counter
import re
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "to", "of", "in", "on", "for",
    "with", "what", "why", "how", "does", "do", "explain", "me", "tell",
    "about", "it", "this", "that", "are", "be", "can"
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [word for word in words if word not in STOPWORDS and len(word) > 2]


def chunk_text(text: str, source: str, max_chars: int = 800) -> list[dict]:
    sections = re.split(r"\n(?=## )", text)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(section) <= max_chars:
            chunks.append({
                "source": source,
                "text": section
            })
        else:
            paragraphs = section.split("\n\n")
            current = ""

            for paragraph in paragraphs:
                if len(current) + len(paragraph) <= max_chars:
                    current += "\n\n" + paragraph if current else paragraph
                else:
                    if current:
                        chunks.append({
                            "source": source,
                            "text": current.strip()
                        })
                    current = paragraph

            if current:
                chunks.append({
                    "source": source,
                    "text": current.strip()
                })

    return chunks


@lru_cache(maxsize=1)
def load_knowledge_base() -> list[dict]:
    if not KNOWLEDGE_BASE_DIR.exists():
        return []

    all_chunks = []

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.md"):
        text = file_path.read_text(encoding="utf-8")
        all_chunks.extend(chunk_text(text, file_path.name))

    return all_chunks


def retrieve_context(question: str, top_k: int = 4) -> list[dict]:
    chunks = load_knowledge_base()
    question_tokens = tokenize(question)

    if not question_tokens:
        return []

    question_counter = Counter(question_tokens)
    scored_chunks = []

    for chunk in chunks:
        chunk_tokens = tokenize(chunk["text"])
        chunk_counter = Counter(chunk_tokens)

        overlap_score = 0

        for token, count in question_counter.items():
            if token in chunk_counter:
                overlap_score += count * chunk_counter[token]

        if overlap_score > 0:
            scored_chunks.append({
                "source": chunk["source"],
                "text": chunk["text"],
                "score": overlap_score
            })

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    return scored_chunks[:top_k]


def build_fallback_answer(question: str, context_chunks: list[dict]) -> str:
    if not context_chunks:
        return (
            "I could not find enough information in the RaceMind AI knowledge base yet. "
            "Try asking about race pace, qualifying, tire degradation, podiums, DNFs, or race strategy."
        )

    best_context = context_chunks[0]["text"]

    return (
        "Based on the RaceMind AI knowledge base:\n\n"
        f"{best_context}\n\n"
        "This answer is generated from local project knowledge. Later, you can improve this by adding embeddings and an LLM."
    )


def answer_with_openai(question: str, context_chunks: list[dict]) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or OpenAI is None:
        return None

    context = "\n\n".join(
        f"Source: {chunk['source']}\n{chunk['text']}"
        for chunk in context_chunks
    )

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are RaceMind AI, an expert MotoGP and motorcycle racing assistant. "
                    "Answer using only the provided context. If the context is not enough, say that clearly. "
                    "Keep the answer useful, technical when helpful, and beginner-friendly."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content


def answer_question(question: str) -> dict:
    clean_question = question.strip()

    if not clean_question:
        return {
            "answer": "Please ask a MotoGP or motorcycle racing question.",
            "sources": []
        }

    context_chunks = retrieve_context(clean_question, top_k=4)
    sources = sorted(set(chunk["source"] for chunk in context_chunks))

    openai_answer = answer_with_openai(clean_question, context_chunks)

    if openai_answer:
        return {
            "answer": openai_answer,
            "sources": sources
        }

    return {
        "answer": build_fallback_answer(clean_question, context_chunks),
        "sources": sources
    }