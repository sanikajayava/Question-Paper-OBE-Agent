import hashlib
import re
from pathlib import Path


class VectorQuestionBank:
    """Persistent local Chroma index with deterministic local embeddings."""

    DIMENSIONS = 384
    COLLECTION_NAME = "question_bank"

    def __init__(self, path=None):
        self.path = Path(path or Path(__file__).resolve().parents[1] /
                         "data" / "chroma_question_bank")
        try:
            import chromadb
        except ImportError as error:
            raise RuntimeError(
                "Chroma is not installed. Install requirements-ai.txt to use "
                "semantic question retrieval."
            ) from error

        self.path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.path))
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @classmethod
    def _embedding(cls, text):
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        vector = [0.0] * cls.DIMENSIONS
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "little") % cls.DIMENSIONS
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign
        norm = sum(value * value for value in vector) ** 0.5
        return [value / norm for value in vector] if norm else vector

    def index_questions(self, questions):
        if not questions:
            return 0
        documents = []
        ids = []
        metadatas = []
        embeddings = []
        for index, question in enumerate(questions):
            text = str(question.get("question_text", "")).strip()
            if not text:
                continue
            ids.append(str(question.get("id", f"question-{index}")))
            documents.append(text)
            metadata = {
                key: value
                for key in ("subject", "exam_type", "batch", "year")
                if (value := question.get(key)) is not None
            }
            metadatas.append(metadata)
            embeddings.append(self._embedding(text))
        if ids:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
        return len(ids)

    def search(self, query, limit=10, where=None):
        result = self.collection.query(
            query_embeddings=[self._embedding(query)],
            n_results=max(1, limit),
            where=where or None,
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            {
                "id": question_id,
                "question_text": document,
                **metadata,
                "distance": distance,
            }
            for question_id, document, metadata, distance in zip(
                ids, documents, metadatas, distances
            )
        ]
