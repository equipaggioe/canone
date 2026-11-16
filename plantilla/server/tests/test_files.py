"""The images and the downloads of the files of the users."""

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image, UnidentifiedImageError

from app.services import files


def photo(orientation: int) -> bytes:
    """Make a 2x1 JPEG with an EXIF orientation and a GPS tag."""
    exif = Image.Exif()
    exif[0x0112] = orientation
    exif[0x8825] = {1: "N"}
    output = BytesIO()
    Image.new("RGB", (2, 1)).save(output, format="JPEG", exif=exif)
    return output.getvalue()


def test_reencode_turns_the_image_and_drops_the_metadata() -> None:
    """An image turned by EXIF comes back upright and without EXIF."""
    with Image.open(BytesIO(files.reencode(photo(6), {"JPEG"}))) as image:
        assert image.size == (1, 2)
        assert not image.getexif()


def test_reencode_rejects_a_format_off_the_list() -> None:
    """A JPEG is refused where the resource takes only PNG."""
    with pytest.raises(UnidentifiedImageError):
        files.reencode(photo(1), {"PNG"})


def test_reencode_rejects_an_image_past_the_pixel_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    """An image past the limit of Pillow fails, even below twice it."""
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1)
    with pytest.raises(Image.DecompressionBombWarning):
        files.reencode(photo(1), {"JPEG"})


def test_sizes_keep_the_ratio_turn_the_image_and_drop_the_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each size is a WebP with its longer side, upright, without EXIF.

    They go in the folder of the id of their row.
    """
    output = BytesIO()
    exif = Image.Exif()
    exif[0x0112] = 6
    exif[0x8825] = {1: "N"}
    Image.new("RGB", (400, 200)).save(output, format="JPEG", exif=exif)
    found = files.sizes(output.getvalue(), {"JPEG"}, {"thumb": 50, "full": 100})
    monkeypatch.setenv("STATE_DIRECTORY", str(tmp_path))
    target = files.store_sizes("9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d", found)
    assert sorted(path.name for path in target.iterdir()) == ["full.webp", "thumb.webp"]
    with Image.open(target / "thumb.webp") as image:
        assert image.format == "WEBP"
        assert image.size == (25, 50)
        assert not image.getexif()
    with Image.open(target / "full.webp") as image:
        assert image.size == (50, 100)


def test_sizes_reject_a_format_off_the_list() -> None:
    """A JPEG is refused where the resource takes only PNG."""
    with pytest.raises(UnidentifiedImageError):
        files.sizes(photo(1), {"PNG"}, {"thumb": 50})


def test_download_is_an_attachment(tmp_path: Path) -> None:
    """A file leaves as an attachment, and of unknown type as binary."""
    path = tmp_path / "file"
    path.write_bytes(b"x")
    response = files.download(path, None, "report.pdf")
    assert response.headers["content-disposition"] == 'attachment; filename="report.pdf"'
    assert response.media_type == "application/octet-stream"
