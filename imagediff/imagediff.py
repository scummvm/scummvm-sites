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
    Compare all frames of a movie between two builds and determine if there are any differences.

    Args:
        src_build (str): The source build name
        cmp_build (str): The comparison build name
        target (str): The target name
        movie (str): The movie name
        screenshots_dir (str): Override for SCREENSHOTS_DIR from config

    Returns:
        bool: True if any frame has differences, False otherwise
    """
    screenshots_dir = screenshots_dir or SCREENSHOTS_DIR
    src_build_path = os.path.join(screenshots_dir, target, src_build)
    cmp_build_path = os.path.join(screenshots_dir, target, cmp_build)

    # Ensure both build paths exist
    if not os.path.exists(src_build_path) or not os.path.exists(cmp_build_path):
        return False

    # Get all frames for this movie in both builds
    src_frames = [f for f in os.listdir(src_build_path)
                  if os.path.isfile(os.path.join(src_build_path, f)) and f.startswith(f"{movie}-")]

    cmp_frames = [f for f in os.listdir(cmp_build_path)
                  if os.path.isfile(os.path.join(cmp_build_path, f)) and f.startswith(f"{movie}-")]

    # If frame counts differ, there's definitely a difference
    if len(src_frames) != len(cmp_frames):
        return True

    # Helper function to extract frame number from filename
    def get_frame_number(filename):
        parts = filename.split('-')
        if len(parts) > 1:
            try:
                return int(parts[1].split('.')[0])
            except ValueError:
                return 0
        return 0

    src_frame_map = {get_frame_number(f): f for f in src_frames}
    cmp_frame_map = {get_frame_number(f): f for f in cmp_frames}

    all_frame_numbers = sorted(set(list(src_frame_map.keys()) + list(cmp_frame_map.keys())))

    if set(src_frame_map.keys()) != set(cmp_frame_map.keys()):
        return True

    for frame_num in all_frame_numbers:
        src_frame = src_frame_map.get(frame_num)
        cmp_frame = cmp_frame_map.get(frame_num)

        if src_frame and cmp_frame:
            src_img_path = os.path.join(src_build_path, src_frame)
            cmp_img_path = os.path.join(cmp_build_path, cmp_frame)

            try:
                diff_result = image_diff(src_img_path, cmp_img_path)

                if diff_result.get('has_diff', False):
                    return True
            except Exception as e:
                print(f"Error comparing frames {src_frame} and {cmp_frame}: {e}")
                return True
        else:
            return True

    return False