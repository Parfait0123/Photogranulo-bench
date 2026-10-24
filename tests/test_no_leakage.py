import json

import pytest

from photogranulo.splits.guard import (
    assert_images_follow_samples,
    assert_no_leakage,
    load_splits,
    load_test_ids,
    make_splits,
    save_splits,
)

FR = {"train": 0.6, "val": 0.2, "test": 0.2}


def test_make_splits_is_deterministic_and_complete():
    ids = [f"S{i}" for i in range(50)]
    a = make_splits(ids, FR, seed=1)
    b = make_splits(ids, FR, seed=1)
    assert a == b
    assert sorted(sum(a.values(), [])) == sorted(ids)
    assert_no_leakage(a)


def test_leakage_detected():
    with pytest.raises(AssertionError):
        assert_no_leakage({"train": ["S1", "S2"], "test": ["S2"]})


def test_images_follow_their_sample():
    splits = {"train": ["S1"], "test": ["S2"]}
    imgs = {"a.jpg": "S1", "b.jpg": "S1", "c.jpg": "S2"}
    out = assert_images_follow_samples(imgs, splits)
    assert out == {"train": ["a.jpg", "b.jpg"], "test": ["c.jpg"]}
    with pytest.raises(AssertionError):
        assert_images_follow_samples({"d.jpg": "S9"}, splits)


def test_tampering_with_frozen_splits_is_detected(tmp_path):
    p = tmp_path / "splits.json"
    save_splits({"train": ["S1"], "test": ["S2"]}, p)
    assert load_splits(p)["test"] == ["S2"]
    data = json.loads(p.read_text())
    data["splits"]["test"] = ["S1"]
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_splits(p)


def test_test_access_is_logged_and_needs_a_reason(tmp_path):
    p, log = tmp_path / "splits.json", tmp_path / "test_access.log"
    save_splits({"train": ["S1"], "test": ["S2"]}, p)
    with pytest.raises(ValueError):
        load_test_ids(p, log, reason="  ")
    assert load_test_ids(p, log, reason="évaluation finale du benchmark") == ["S2"]
    assert "évaluation finale" in log.read_text(encoding="utf-8")
