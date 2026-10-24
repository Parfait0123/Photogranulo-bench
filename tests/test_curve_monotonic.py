from photogranulo.audit.curves import check_psd_curve

D = [0.08, 0.16, 0.315, 0.63, 1.25]


def test_valid_curve():
    assert check_psd_curve(D, [2, 10, 40, 80, 100]) == []


def test_flat_curve_is_valid():
    assert check_psd_curve(D, [100] * 5) == []


def test_decreasing_curve_detected():
    assert any("décroissante" in m for m in check_psd_curve(D, [2, 10, 9, 80, 100]))


def test_out_of_range_detected():
    assert any("hors" in m for m in check_psd_curve(D, [-1, 10, 40, 80, 101]))


def test_unsorted_openings_and_length_mismatch():
    assert check_psd_curve([1, 0.5], [1, 2])
    assert check_psd_curve(D, [1, 2])
