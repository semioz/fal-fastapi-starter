import tempfile
from typing import Optional

def is_valid_image(file) -> bool:
    allowed_content_types = ["image/jpeg", "image/png", "image/jpg"]
    return file.content_type in allowed_content_types

def parse_fal_output(output) -> Optional[str]:
    if hasattr(output, "read"):
        image_bytes = output.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(image_bytes)
            return tmp_file.name

    if isinstance(output, str) and output.strip().startswith(("http://", "https://")):
        return output.strip()

    if isinstance(output, list):
        for item in output:
            if isinstance(item, str) and item.strip().startswith(("http://", "https://")):
                return item.strip()
            if isinstance(item, dict) and "url" in item:
                return item["url"]

    if isinstance(output, dict):
        # Handle Fal AI response format: {'images': [{'url': '...', ...}], 'seed': ...}
        if "images" in output and isinstance(output["images"], list) and output["images"]:
            first_image = output["images"][0]
            if isinstance(first_image, dict) and "url" in first_image:
                return first_image["url"]
        
        # Handle other common formats
        nested = output.get("output") or output.get("url")
        if isinstance(nested, str) and nested.strip().startswith(("http://", "https://")):
            return nested.strip()
        if isinstance(nested, list):
            for item in nested:
                if isinstance(item, str) and item.strip().startswith(("http://", "https://")):
                    return item.strip()
                if isinstance(item, dict) and "url" in item:
                    return item["url"]
    return None