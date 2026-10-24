import pytest
from copilot.cv_parser import read_cv


def test_read_txt_cv(tmp_path):
    f = tmp_path / "cv.txt"
    f.write_text("Wakib\nPython, PyTorch", encoding="utf-8")
    assert "PyTorch" in read_cv(str(f))


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        read_cv("nope.pdf")


def test_unsupported_type(tmp_path):
    f = tmp_path / "cv.docx"
    f.write_text("x")
    with pytest.raises(ValueError):
        read_cv(str(f))
