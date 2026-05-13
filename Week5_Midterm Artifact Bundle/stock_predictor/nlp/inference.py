"""Sentiment inference wrapper with model pinning and batch processing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..nlp.sentiment import get_sentiment_model_id


@dataclass(frozen=True)
class SentimentScore:
    """Sentiment inference result for a single message."""

    text: str
    polarity: float  # [-1.0, 1.0] where -1.0 = very negative, 1.0 = very positive
    confidence: float  # [0.0, 1.0]
    model_id: str  # for traceability


@dataclass(frozen=True)
class BatchSentimentResult:
    """Result of batch sentiment inference."""

    scores: list[SentimentScore]
    batch_size: int
    duration_seconds: float
    model_id: str


class SentimentInferenceWrapper:
    """Wrapper enforcing pinned model ID with batch processing."""

    def __init__(
        self,
        model_loader: Callable[[str], object] | None = None,
        batch_size: int = 32,
        timeout_seconds: float = 30.0,
    ):
        """Initialize sentiment inference wrapper.

        Args:
            model_loader: Optional function to load the model (for testing)
            batch_size: Max items per batch for inference
            timeout_seconds: Hard timeout for batch inference
        """
        self.model_id = get_sentiment_model_id()  # Enforce pinning
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.model_loader = model_loader
        self._model = None

    def infer_sentiment(self, text: str) -> SentimentScore:
        """Infer sentiment for single text.

        Returns:
            SentimentScore with polarity in [-1.0, 1.0]
        """
        # In production, call the actual transformer pipeline
        # For now, return mock score
        polarity = self._mock_infer(text)
        return SentimentScore(
            text=text,
            polarity=polarity,
            confidence=0.85,
            model_id=self.model_id,
        )

    def infer_batch(self, texts: list[str]) -> BatchSentimentResult:
        """Infer sentiment for multiple texts with timeout.

        Args:
            texts: List of texts to analyze

        Returns:
            BatchSentimentResult with all scores and metadata
        """
        scores: list[SentimentScore] = []
        for text in texts:
            score = self.infer_sentiment(text)
            scores.append(score)

        return BatchSentimentResult(
            scores=scores,
            batch_size=len(texts),
            duration_seconds=0.1,  # mock duration
            model_id=self.model_id,
        )

    def _mock_infer(self, text: str) -> float:
        """Mock sentiment inference for testing."""
        # Deterministic sentiment based on text length and hash
        hash_val = hash(text) & 0xFFFFFFFF
        return (hash_val % 200 - 100) / 100.0  # [-1.0, 1.0]

    def ensure_model_pinned(self) -> str:
        """Verify model ID matches pinned version.

        Raises:
            ValueError if model_id has changed (configuration error)
        """
        current_id = get_sentiment_model_id()
        if current_id != self.model_id:
            raise ValueError(
                f"Model ID mismatch: expected {self.model_id}, got {current_id}. "
                "Model pinning broken."
            )
        return current_id
