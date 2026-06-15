import os
import base64
from io import BytesIO

from PIL import Image, ImageChops

from config import SCREENSHOTS_DIR

def encode_image(image):
    """Encode an image to a base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def image_diff(src_img_path, cmp_img_path):
    """
    Compute the difference between two images and return the results.
    """
    try:
        src_img = Image.open(src_img_path)
        cmp_img = Image.open(cmp_img_path)
        diff_img = ImageChops.difference(src_img, cmp_img).convert('RGB')

        has_diff = diff_img.getbbox() is not None

        return {
            'src_img_data': encode_image(src_img),
            'cmp_img_data': encode_image(cmp_img),
            'diff_img_data': encode_image(diff_img) if has_diff else None,
            'has_diff': has_diff
        }
    except IOError:
        return {}

def list_movie_prefixes(build_path):
    """Return sorted movie filename prefixes present in a build directory."""
    prefixes = set()
    if not os.path.isdir(build_path):
        return []
    for name in os.listdir(build_path):
        if name.endswith(".png") and "-" in name:
            prefixes.add(name.rsplit("-", 1)[0])
    return sorted(prefixes)


def find_baseline_build(screenshots_dir, target, current_build):
    """Return the highest prior build number that has stored screenshots."""
    target_path = os.path.join(screenshots_dir, target)
    if not os.path.isdir(target_path):
        return None
    try:
        current_number = int(current_build)
    except ValueError:
        return None
    candidates = []
    for entry in os.listdir(target_path):
        if not os.path.isdir(os.path.join(target_path, entry)):
            continue
        try:
            build_number = int(entry)
        except ValueError:
            continue
        if build_number < current_number:
            candidates.append(build_number)
    return str(max(candidates)) if candidates else None


def movie_diff(src_build, cmp_build, target, movie, screenshots_dir=None):
    """
    Determine if a movie differs between two builds by checking file presence.

    The Director engine only saves a screenshot when it detects a change vs the
    previous build (using pixel comparison with a threshold). So if a frame file
    exists in a build, the engine already confirmed it differs. No PIL comparison
    needed here, file presence IS the diff signal.
    """
    screenshots_dir = screenshots_dir or SCREENSHOTS_DIR
    src_build_path = os.path.join(screenshots_dir, target, src_build)
    cmp_build_path = os.path.join(screenshots_dir, target, cmp_build)

    if not os.path.exists(src_build_path) or not os.path.exists(cmp_build_path):
        return False

    cmp_frames = {f for f in os.listdir(cmp_build_path) if f.startswith(f"{movie}-")}

    # The engine only saves a screenshot file when it detects a change vs the previous build.
    # So any file in cmp_build means cmp_build differs from src_build.
    return len(cmp_frames) > 0

