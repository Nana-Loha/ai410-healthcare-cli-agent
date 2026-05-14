from Week5_midterm.stock_predictor.nlp.sentiment import get_sentiment_model_id
from Week5_midterm.stock_predictor.nlp.inference import (
    SentimentInferenceWrapper,
    SentimentScore,
)


def test_sentiment_model_is_pinned() -> None:
    assert (
        get_sentiment_model_id()
        == "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    )


def test_sentiment_inference_single() -> None:
    """Test single text sentiment inference."""
    wrapper = SentimentInferenceWrapper()
    score = wrapper.infer_sentiment("Great earnings report!")

    assert isinstance(score, SentimentScore)
    assert -1.0 <= score.polarity <= 1.0
    assert 0.0 <= score.confidence <= 1.0
    assert score.model_id == "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"


def test_sentiment_inference_batch() -> None:
    """Test batch sentiment inference."""
    wrapper = SentimentInferenceWrapper(batch_size=4)
    texts = [
        "Positive news for the stock",
        "Negative market conditions",
        "Neutral report released",
        "Outstanding performance",
    ]

    result = wrapper.infer_batch(texts)

    assert len(result.scores) == 4
    assert result.batch_size == 4
    assert result.model_id == "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    assert all(-1.0 <= s.polarity <= 1.0 for s in result.scores)


def test_sentiment_model_pinning() -> None:
    """Test that model ID pinning is enforced."""
    wrapper = SentimentInferenceWrapper()
    pinned_id = wrapper.ensure_model_pinned()

    assert pinned_id == "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    assert wrapper.model_id == pinned_id


def test_sentiment_inference_empty_batch() -> None:
    """Test batch inference with empty list."""
    wrapper = SentimentInferenceWrapper()
    result = wrapper.infer_batch([])

    assert len(result.scores) == 0
    assert result.batch_size == 0


def test_sentiment_inference_large_batch() -> None:
    """Test batch inference scales with list size."""
    wrapper = SentimentInferenceWrapper(batch_size=100)
    texts = [f"Text {i}" for i in range(100)]

    result = wrapper.infer_batch(texts)

    assert len(result.scores) == 100
    assert result.batch_size == 100
