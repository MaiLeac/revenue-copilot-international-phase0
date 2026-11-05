from tools.trading_ctl import format_status


def test_old_running_label_is_not_reported_as_live():
    state = {
        "status": "RUNNING", "command": "start",
        "last_heartbeat_utc": "2020-01-01T00:00:00+00:00",
        "account": {"trade_mode_label": "DEMO"},
    }
    assert "STALE / NOT VERIFIED RUNNING" in format_status(state)
