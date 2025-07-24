import tempfile

from fastapi import HTTPException


def is_valid_image(file) -> bool:
    allowed_content_types = ["image/jpeg", "image/png", "image/jpg"]
    return file.content_type in allowed_content_types


def handle_fal_error(error: Exception) -> HTTPException:
    error_str = str(error)

    if "image_too_small" in error_str or "Image dimensions are too small" in error_str:
        return HTTPException(
            status_code=400,
            detail="Image is too small!",
        )
    if "image_too_large" in error_str:
        return HTTPException(
            status_code=400,
            detail="Image is too large!",
        )
    if "image_load_error" in error_str:
        return HTTPException(
            status_code=400,
            detail="Unsupported image format!",
        )

    return HTTPException(status_code=500, detail=str(error))


def parse_fal_output(output) -> str | None:
    if hasattr(output, "read"):
        image_bytes = output.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(image_bytes)
            return tmp_file.name

    if isinstance(output, dict):
        if (
            "images" in output
            and isinstance(output["images"], list)
            and output["images"]
        ):
            first_image = output["images"][0]
            if isinstance(first_image, dict) and "url" in first_image:
                return first_image["url"]

        nested = output.get("output") or output.get("url")
        if isinstance(nested, str) and nested.strip().startswith(
            ("http://", "https://")
        ):
            return nested.strip()
        if isinstance(nested, list):
            for item in nested:
                if isinstance(item, str) and item.strip().startswith(
                    ("http://", "https://")
                ):
                    return item.strip()
                if isinstance(item, dict) and "url" in item:
                    return item["url"]
    return None
