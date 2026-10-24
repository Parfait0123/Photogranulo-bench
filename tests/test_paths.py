import pytest

from photogranulo.utils.paths import REPO_ROOT, load_paths

CFG = """
profiles:
  local: {data_root: data, results_root: results}
  big:
    data_root: /mnt/d
    results_root: /mnt/r
    extra: [checkpoints]
    overrides: {raw: /mnt/in}
  later: {data_root: TODO, results_root: TODO}
"""


@pytest.fixture
def cfg(tmp_path):
    p = tmp_path / "paths.yaml"
    p.write_text(CFG)
    return p


def test_local_paths_are_relative_to_repo(cfg):
    p = load_paths("local", cfg)
    assert p["raw"] == REPO_ROOT / "data" / "raw"
    assert p["results"] == REPO_ROOT / "results"


def test_extra_and_overrides(cfg):
    p = load_paths("big", cfg)
    assert str(p["checkpoints"]) == "/mnt/d/checkpoints"
    assert str(p["raw"]) == "/mnt/in" and str(p["interim"]) == "/mnt/d/interim"


def test_env_variable_selects_profile(cfg, monkeypatch):
    monkeypatch.setenv("PHOTOGRANULO_ENV", "big")
    assert str(load_paths(config=cfg)["data_root"]) == "/mnt/d"


def test_unknown_and_todo_profiles_fail(cfg):
    with pytest.raises(KeyError):
        load_paths("nope", cfg)
    with pytest.raises(ValueError):
        load_paths("later", cfg)


def test_shipped_config_is_valid():
    assert load_paths("local")["raw"].name == "raw"
