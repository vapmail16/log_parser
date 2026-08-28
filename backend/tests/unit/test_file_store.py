from app.core.file_store import JsonFileStore
from app.core.models import Run


def test_save_and_load_latest_run(tmp_store_dir, sample_run):
    store = JsonFileStore(tmp_store_dir)
    store.save_run(sample_run)
    loaded = store.get_latest()
    assert loaded is not None
    assert loaded.id == sample_run.id
    assert len(loaded.events) == len(sample_run.events)
    assert loaded.events[0].display_id == "786712011"


def test_save_replaces_previous_run(tmp_store_dir, sample_run, sample_events):
    store = JsonFileStore(tmp_store_dir)
    store.save_run(sample_run)
    next_run = Run(
        id="run-2",
        domain="trade",
        source_path="/other",
        status="completed",
        events=sample_events[:1],
    )
    store.save_run(next_run)
    loaded = store.get_latest()
    assert loaded is not None
    assert loaded.id == "run-2"
    assert len(loaded.events) == 1


def test_get_event_and_missing(tmp_store_dir, sample_run):
    store = JsonFileStore(tmp_store_dir)
    store.save_run(sample_run)
    found = store.get_event("trade:SLT:SL_ALTER_TRADE:786712011")
    assert found is not None
    assert found.group_id == "HH0Y9V9"
    assert store.get_event("missing") is None


def test_empty_store_returns_none(tmp_store_dir):
    store = JsonFileStore(tmp_store_dir)
    assert store.get_latest() is None
