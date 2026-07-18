import logging

from openai import OpenAI

from app.core.config import EMBEDDING_DIMENSION, OPENAI_EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates OpenAI embeddings for batches of file content.

    One instance is meant to be reused across all batches of a single analysis
    job, so the underlying HTTP client/connection is created once (per OpenAI
    SDK guidance) instead of per batch.
    """

    def __init__(self, repository_id: str):
        self.repository_id = repository_id
        self._client = OpenAI()

    def generate(self, batch: list[dict]) -> dict[str, list[float]]:
        """batch: [{"id": ..., "content": ...}, ...] -> {id: embedding}. Non-fatal on failure."""
        try:
            texts = [item["content"] for item in batch]
            response = self._client.embeddings.create(
                model=OPENAI_EMBEDDING_MODEL,
                input=texts,
                dimensions=EMBEDDING_DIMENSION,
                safety_identifier=f"repo:{self.repository_id}",
            )
            return {
                batch[i]["id"]: emb_data.embedding
                for i, emb_data in enumerate(response.data)
            }
        except Exception as e:
            logger.warning(f"Embedding generation failed (non-fatal): {e}")
            return {}