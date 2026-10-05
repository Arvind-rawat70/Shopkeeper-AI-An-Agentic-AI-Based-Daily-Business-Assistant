from database import logger


def test_write_log_accepts_response_time_ms(monkeypatch, tmp_path):
    db_path = tmp_path / "logs.sqlite"
    monkeypatch.setattr(logger, "DB_PATH", db_path)
    logger.init_db()

    logger.write_log(
        "2026-10-05T00:00:00Z",
        "INFO",
        "chatbot_response",
        "hello",
        {"source": "ui"},
        response_time_ms=123.45,
    )

    rows = logger.read_logs(limit=1)
    assert rows[0]["meta"]["response_time_ms"] == 123.45
