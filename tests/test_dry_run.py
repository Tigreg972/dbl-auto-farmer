from app import build_runtime


def test_dry_run_never_clicks():
    clicks = []
    runtime = build_runtime(
        dry_run=True,
        click_fn=lambda x, y: clicks.append((x, y)),
        window_provider=lambda: [],
    )

    runtime.process_once(frame=None, now=1.0)

    assert clicks == []
