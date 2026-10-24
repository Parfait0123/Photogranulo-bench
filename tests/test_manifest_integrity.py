from photogranulo.data.manifest import (
    build_manifest,
    count_by_extension,
    verify_manifest,
)


def _make_tree(root):
    (root / "soil_image").mkdir(parents=True)
    (root / "soil_image" / "a.jpg").write_bytes(b"aaaa")
    (root / "soil_image" / "b.jpg").write_bytes(b"bbbbbb")
    (root / "courbes.xlsx").write_bytes(b"xlsx")


def test_build_then_verify_ok(tmp_path):
    root = tmp_path / "raw"
    _make_tree(root)
    m = tmp_path / "m.csv"
    assert build_manifest(root, m) == 3
    res = verify_manifest(root, m)
    assert res == {"missing": [], "extra": [], "corrupted": []}


def test_detects_missing_extra_and_corrupted(tmp_path):
    root = tmp_path / "raw"
    _make_tree(root)
    m = tmp_path / "m.csv"
    build_manifest(root, m)

    (root / "soil_image" / "a.jpg").unlink()
    (root / "soil_image" / "b.jpg").write_bytes(b"bbbbbX")  # même taille, autre contenu
    (root / "nouveau.jpg").write_bytes(b"z")

    res = verify_manifest(root, m)
    assert res["missing"] == ["soil_image/a.jpg"]
    assert res["corrupted"] == ["soil_image/b.jpg"]
    assert res["extra"] == ["nouveau.jpg"]


def test_count_by_extension(tmp_path):
    root = tmp_path / "raw"
    _make_tree(root)
    c = count_by_extension(root)
    assert c[".jpg"] == 2 and c[".xlsx"] == 1
