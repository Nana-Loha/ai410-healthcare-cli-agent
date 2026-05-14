from Week5_midterm.stock_predictor.features.alpha import alpha_sam


def test_alpha_sam_returns_zero_when_volume_not_confirmed() -> None:
    result = alpha_sam(
        close_t=101.0,
        sma20=100.0,
        sentiment_t=0.7,
        current_volume=1000.0,
        volume_sma20=1000.0,
        min_volume_ratio=1.1,
    )
    assert result == 0.0


def test_alpha_sam_positive_signal_with_confirmed_volume() -> None:
    result = alpha_sam(
        close_t=102.0,
        sma20=100.0,
        sentiment_t=0.5,
        current_volume=1300.0,
        volume_sma20=1000.0,
        min_volume_ratio=1.1,
    )
    assert result > 0.0


def test_alpha_sam_raises_for_invalid_sma() -> None:
    try:
        alpha_sam(
            close_t=100.0,
            sma20=0.0,
            sentiment_t=0.1,
            current_volume=1200.0,
            volume_sma20=1000.0,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "sma20 must be positive" in str(exc)
