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


def test_read_cv_bytes_txt_and_errors():
    from copilot.cv_parser import read_cv_bytes

    assert "Python" in read_cv_bytes(b"Wakib knows Python", "cv.txt")
    with pytest.raises(ValueError):
        read_cv_bytes(b"x", "cv.docx")
    with pytest.raises(ValueError):
        read_cv_bytes(b"   ", "cv.txt")


def test_read_cv_bytes_pdf():
    import pymupdf

    from copilot.cv_parser import read_cv_bytes

    doc = pymupdf.open()
    doc.new_page().insert_text((72, 72), "Wakib - Python, PyTorch")
    assert "PyTorch" in read_cv_bytes(doc.tobytes(), "cv.pdf")
