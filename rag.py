import os

import chromadb
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer

from sheets import fetch_postulaciones

EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
GEN_MODEL = "claude-haiku-4-5-20251001"
TOP_K = 8

_embedder = SentenceTransformer(EMBED_MODEL)


def _row_to_text(row: dict) -> str:
    return (
        f"Empresa: {row['Empresa']}. Puesto: {row['Puesto']}. "
        f"Fuente: {row['Fuente']}. Estado: {row['Estado']}. "
        f"Fecha: {row['Fecha']}. Salario/Rango: {row['Salario']}. "
        f"Contacto: {row['Contacto']}. Proxima accion: {row['Proxima_accion']}. "
        f"Notas: {row['Notas']}."
    )


def build_index():
    records = fetch_postulaciones()
    if not records:
        return None, []

    docs = [_row_to_text(r) for r in records]
    embeddings = _embedder.encode(docs).tolist()

    client = chromadb.EphemeralClient()
    collection = client.create_collection("postulaciones")
    collection.add(
        ids=[str(i) for i in range(len(docs))],
        documents=docs,
        embeddings=embeddings,
    )
    return collection, records


def retrieve(collection, question: str, k: int = TOP_K) -> list[str]:
    query_embedding = _embedder.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=min(k, collection.count()))
    return results["documents"][0]


def answer(question: str, context_docs: list[str]) -> str:
    context = "\n".join(f"- {doc}" for doc in context_docs)
    client = Anthropic()
    message = client.messages.create(
        model=GEN_MODEL,
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                "Eres un asistente que responde preguntas sobre el historial de "
                "postulaciones laborales de Junior, usando SOLO el contexto de abajo. "
                "Responde en español, directo y breve. Si el contexto no alcanza para "
                "responder, dilo explícitamente en vez de inventar.\n\n"
                f"Contexto:\n{context}\n\n"
                f"Pregunta: {question}"
            ),
        }],
    )
    return message.content[0].text
