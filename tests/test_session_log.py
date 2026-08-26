from dbl_farmer.logging.session_log import SessionLogger


def test_summary_always_reports_zero_cc_spent(tmp_path):
    logger = SessionLogger(tmp_path)
    logger.stats.energy_used = 20
    logger.stats.skip_tickets_used = 5
    logger.stats.successful_stages = 3

    text = logger.summary()

    assert "Energy used: 20" in text
    assert "Skip Tickets used: 5" in text
    assert "Successful stages: 3" in text
    assert "Chrono Crystals spent: 0" in text


def test_event_writes_human_readable_log(tmp_path):
    logger = SessionLogger(tmp_path)
    logger.event("HOME detected", confidence=0.94)

    text = logger.log_path.read_text(encoding="utf-8")
    assert "HOME detected" in text
    assert "confidence=0.94" in text
