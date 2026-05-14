from Week5_midterm.stock_predictor.data.ingestion import SocialMessage, filter_social_stream


def test_bot_filter_keeps_legit_message() -> None:
    message = SocialMessage(
        symbol="AAPL",
        text="$AAPL breakout on earnings",
        account_age_days=400,
        posts_per_day=3,
        follower_following_ratio=1.2,
        duplicate_burst_count=0,
    )
    kept, audit = filter_social_stream([message])
    assert len(kept) == 1
    assert audit[0].keep is True


def test_bot_filter_removes_high_risk_message() -> None:
    message = SocialMessage(
        symbol="TSLA",
        text="$TSLA moon soon",
        account_age_days=7,
        posts_per_day=120,
        follower_following_ratio=0.05,
        duplicate_burst_count=5,
        contains_spam_link=True,
    )
    kept, audit = filter_social_stream([message])
    assert len(kept) == 0
    assert audit[0].keep is False
    assert audit[0].score >= 2.0
