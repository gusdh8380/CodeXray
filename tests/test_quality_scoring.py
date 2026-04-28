from codexray.quality.scoring import score_to_grade


def test_boundary_a() -> None:
    assert score_to_grade(90) == "A"
    assert score_to_grade(89) == "B"


def test_boundary_b() -> None:
    assert score_to_grade(75) == "B"
    assert score_to_grade(74) == "C"


def test_boundary_c() -> None:
    assert score_to_grade(60) == "C"
    assert score_to_grade(59) == "D"


def test_boundary_d() -> None:
    assert score_to_grade(40) == "D"
    assert score_to_grade(39) == "F"


def test_full_scores() -> None:
    assert score_to_grade(100) == "A"
    assert score_to_grade(0) == "F"
