import os
import json
import sys
import base64
from io import BytesIO

# config.py lives next to this file; make it importable no matter where we
# are imported from (buildbot master, worker step, or standalone).
_imagediff_dir = os.path.dirname(__file__)
if _imagediff_dir not in sys.path:
    sys.path.insert(0, _imagediff_dir)

from PIL import Image, ImageChops

from flask import Flask, render_template, jsonify, url_for, send_from_directory, request

from config import CACHE_DIR, SCREENSHOTS_DIR

app = Flask(__name__)

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


# String decoding functions
def unescape_string(s: str) -> str:
    """unescape strings"""
    orig_name = ""
    s_iter = iter(s)
    hi = next(s_iter, None)
    while hi is not None:
        if hi == "\x81":
            low = next(s_iter, None)
            assert low is not None, "Error decoding string"
            if low == "\x79":
                orig_name += "\x81"
            else:
                orig_name += chr(ord(low) - 0x80)
        else:
            orig_name += hi
        hi = next(s_iter, None)
    return orig_name

def decode_string(orig: str) -> str:
    """
    Decode punyencoded strings
    """
    if not orig.startswith("xn--"):
        return orig

    st = orig[4:].encode("ascii").decode("punycode")
    return unescape_string(st)

# cache functions
def get_cache_page_path(target, page):
    """Generates path: cache/<target>/page_<page>.json"""
    target_dir = os.path.join(CACHE_DIR, target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return os.path.join(target_dir, f"page_{page}.json")

def load_target_cache(target, page):
    """Loads cache from disk for a specific target and page."""
    path = get_cache_page_path(target, page)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data if data else None
    except (json.JSONDecodeError, IOError):
        return None

def save_target_cache(target, page, cache):
    """Saves the calculated data to the specific page file."""
    path = get_cache_page_path(target, page)
    with open(path, "w") as f:
        json.dump(cache, f)

def get_frame_cache_path(target):
    target_dir = os.path.join(CACHE_DIR, target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return os.path.join(target_dir, "frame_diffs.json")

def load_frame_cache(target):
    path = get_frame_cache_path(target)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def save_frame_cache(target, cache):
    path = get_frame_cache_path(target)
    with open(path, "w") as f:
        json.dump(cache, f)

# save string keys for frame-level diffs if needed
def make_cache_key(target, build1, build2, movie, frame):
    return f"{target}_{build1}_{build2}_{movie}_{frame}"

def get_frame_number(filename):
    """Extract frame number from filename."""
    parts = filename.split('-')
    if len(parts) > 1:
        try:
            return int(parts[1].rsplit('.')[0])
        except ValueError:
            return 0



def get_pagination_pages(page, total_pages, window=2):
    """Return list of page numbers with None for ellipsis gaps."""
    pages = set([1, total_pages])
    for i in range(max(1, page - window), min(total_pages, page + window) + 1):
        pages.add(i)
    result = []
    prev = None
    for p in sorted(pages):
        if prev is not None and p - prev > 1:
            result.append(None)
        result.append(p)
        prev = p
    return result


def get_sorted_builds(target_path, reverse=True):
    """Get sorted list of builds for a target."""
    builds = [b for b in os.listdir(target_path)
              if os.path.isdir(os.path.join(target_path, b))]
    # Sort numerically to handle build IDs correctly (e.g., "2" < "245" < "2452")
    try:
        return sorted(builds, key=lambda x: int(x), reverse=reverse)
    except ValueError:
        # Fall back to string sort if build IDs are not numeric
        return sorted(builds, reverse=reverse)

def collect_movie_frames(target_path, builds):
    """Collect all movie frames information for all builds."""
    all_movies = set()
    build_movie_frames = {}
    build_files = {}

    # Pre-collect file information to avoid multiple directory reads
    for build in builds:
        build_path = os.path.join(target_path, build)
        build_files[build] = os.listdir(build_path)

    # Process movie and frame data
    for build in builds:
        build_movie_frames[build] = {}

        for file in build_files[build]:
            if not os.path.isfile(os.path.join(target_path, build, file)):
                continue
            if "-" not in file:
                continue


            movie_name, frame_part = file.rsplit("-", 1)
            frame_num = frame_part.split('.')[0]

            if movie_name not in build_movie_frames[build]:
                build_movie_frames[build][movie_name] = []

            build_movie_frames[build][movie_name].append(frame_num)
            all_movies.add(movie_name)

    return all_movies, build_movie_frames, build_files

def find_first_build_for_movies(all_movies, builds_ascending, build_movie_frames):
    """Find the first build where each movie appears."""
    first_build_for_movie = {}
    for movie in all_movies:
        for build in builds_ascending:
            if movie in build_movie_frames.get(build, {}):
                first_build_for_movie[movie] = build
                break
    return first_build_for_movie

def calculate_reference_builds(all_movies, builds, build_movie_frames):
    """Calculate reference builds for each movie in each build."""
    movie_reference_builds = {}
    for movie in all_movies:
        movie_reference_builds[movie] = {}
        for i, current_build in enumerate(builds):
            has_in_current = movie in build_movie_frames.get(current_build, {})

            if not has_in_current:
                reference_build = None
                for j in range(i+1, len(builds)):
                    if movie in build_movie_frames.get(builds[j], {}):
                        reference_build = builds[j]
                        break
                movie_reference_builds[movie][current_build] = reference_build
    return movie_reference_builds

def get_movie_frames(build_path, movie_prefix=None):
    """Get all frames for a movie in a build path."""
    all_files = [f for f in os.listdir(build_path)
                 if os.path.isfile(os.path.join(build_path, f))]

    if movie_prefix:
        # Filter files for specific movie
        movie_files = [f for f in all_files if f.startswith(f"{movie_prefix}-")]
    else:
        # Get all movie files
        movie_files = [f for f in all_files if "-" in f]

    return sorted(movie_files, key=get_frame_number)

def extract_movie_names(files):
    """Extract unique movie names from a list of files."""
    movies = set()
    for file in files:
        if "-" in file:
            movie_name = file.rsplit("-", 1)[0]
            movies.add(movie_name)
    return movies

def create_frame_map(frames):
    """Create a map of frame numbers to filenames."""
    return {get_frame_number(f): f for f in frames}

@app.route('/')
@app.route('/index.html')
def index():
    targets = [d for d in os.listdir(SCREENSHOTS_DIR)
               if os.path.isdir(os.path.join(SCREENSHOTS_DIR, d))]

    return render_template('index.html', targets=targets)


@app.route('/target/<target>')
def target_detail(target):
    target_path = os.path.join(SCREENSHOTS_DIR, target)

    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        return "Target not found", 404

    builds = get_sorted_builds(target_path, reverse=False)
    page_size = 20
    total_pages = max(1, (len(builds) + page_size - 1) // page_size)
    page_param = request.args.get('page')
    page = int(page_param) if page_param is not None else total_pages
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    paginated_builds = builds[start:end]
    pagination_pages = get_pagination_pages(page, total_pages)

    cache_data = load_target_cache(target, page)

    return render_template('target.html',
        target=target,
        display_target=decode_string(target),
        builds=paginated_builds,
        page=page,
        total_pages=total_pages,
        pagination_pages=pagination_pages,
        cache_data=cache_data)


# Handle time-consuming data calculations
@app.route('/api/target_data/<target>')
def target_data_api(target):
    page = int(request.args.get('page', 1))
    page_size = 20

    cached_data = load_target_cache(target, page)
    if cached_data:
        return jsonify(cached_data)

    target_path = os.path.join(SCREENSHOTS_DIR, target)

    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        return jsonify({"error": "Target not found"}), 404

    builds = get_sorted_builds(target_path,reverse=False)
    builds_ascending = get_sorted_builds(target_path, reverse=False)

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    current_page_builds = builds[start_index:end_index]
    # Include previous build (from previous page) for comparison continuity
    process_start = start_index - 1 if start_index > 0 else start_index
    builds_to_process = builds[process_start:end_index + 1] if end_index < len(builds) else builds[process_start:end_index]

    # Collect movie frame data
    all_movies, build_movie_frames, _ = collect_movie_frames(target_path,builds)

    # Calculate first build for each movie
    first_build_for_movie = find_first_build_for_movies(
        all_movies, builds_ascending, build_movie_frames)

    # Pre-compute for each movie the sorted list of builds where it appears
    movie_builds_index = {}
    for movie in all_movies:
        movie_builds_index[movie] = [b for b in builds_ascending if movie in build_movie_frames.get(b, {})]

    # Calculate reference builds searching ALL builds globally
    movie_reference_builds = {}
    for movie in all_movies:
        movie_reference_builds[movie] = {}
        movie_build_list = movie_builds_index[movie]
        for current_build in builds_to_process:
            has_in_current = movie in build_movie_frames.get(current_build, {})
            current_frames = build_movie_frames.get(current_build, {}).get(movie, [])

            if not has_in_current:
                # Search ALL builds before current_build for the most recent one with this movie
                reference_build = None
                try:
                    current_number = int(current_build)
                except ValueError:
                    current_number = None
                if current_number is not None:
                    for b in reversed(movie_build_list):
                        try:
                            if int(b) < current_number:
                                reference_build = b
                                break
                        except ValueError:
                            continue
                movie_reference_builds[movie][current_build] = {
                    'build': reference_build,
                    'frames': build_movie_frames.get(reference_build, {}).get(movie, []) if reference_build else []
                }
            else:
                # Current build has the movie, find a reference build with matching frames
                reference_data = {
                    'build': None,
                    'frames': current_frames
                }
                try:
                    current_number = int(current_build)
                except ValueError:
                    current_number = None
                if current_number is not None:
                    for b in reversed(movie_build_list):
                        try:
                            if int(b) < current_number:
                                next_frames = build_movie_frames.get(b, {}).get(movie, [])
                                common_frames = set(current_frames).intersection(set(next_frames))
                                if common_frames:
                                    reference_data = {
                                        'build': b,
                                        'frames': list(common_frames)
                                    }
                                    break
                        except ValueError:
                            continue
                movie_reference_builds[movie][current_build] = reference_data

    def get_image_diff(current_build, prev_build, movie, frame):
        current_frame_path = os.path.join(target_path, current_build, f"{movie}-{frame}.png")
        prev_frame_path = os.path.join(target_path, prev_build, f"{movie}-{frame}.png")
        # File presence is the diff signal, engine only saves when it detects a change
        has_diff = os.path.exists(current_frame_path) and os.path.exists(prev_frame_path)
        return {'has_diff': has_diff}

    # Modified movie difference function to only compare specified frames
    def get_movie_diff_for_frames(current_build, reference_build, target, movie, frames_to_compare):
        if not frames_to_compare:
            return False  # No frames to compare

        has_any_diff = False
        for frame in frames_to_compare:
            diff_result = get_image_diff(current_build, reference_build, movie, frame)
            if diff_result.get('has_diff', False):
                has_any_diff = True
                break

        return has_any_diff

    # Pre-calculate movie difference results


    # def get_movie_diff_cached(current_build, prev_build, target, movie):
    #     cache_key = (current_build, prev_build, target, movie)
    #     if cache_key not in movie_diff:
    #         movie_diff_cache[cache_key] = movie_diff(current_build, prev_build, target, movie)
    #         save_movie_diff_cache(movie_diff_cache, target)
    #     return movie_diff_cache[cache_key]

    movies = sorted(list(all_movies))

    # Context build is used only for determining "previous" state,
    # but NOT included in output (output must match current_page_builds columns)
    context_build = builds[start_index - 1] if start_index > 0 else None

    continuous_bars = {}

    # Create continuous bars for visualization
    for movie in movies:
        continuous_bars[movie] = []
        movie_build_list = movie_builds_index[movie]

        # Find the next build (globally) where this movie reappears after a given build
        def find_next_appearance(after_build):
            try:
                after_num = int(after_build)
            except ValueError:
                return None
            for b in movie_build_list:
                try:
                    if int(b) > after_num:
                        return b
                except ValueError:
                    continue
            return None

        for i, current_build in enumerate(current_page_builds):
            # Determine the effective previous build for comparison
            if i == 0:
                prev_build = context_build
            else:
                prev_build = current_page_builds[i - 1]

            has_in_current = movie in build_movie_frames.get(current_build, {})
            current_frames = build_movie_frames.get(current_build, {}).get(movie, [])

            prev_frames = []
            if prev_build:
                prev_frames = build_movie_frames.get(prev_build, {}).get(movie, [])

            has_in_prev = len(prev_frames) > 0 if prev_build else False
            is_first_build = (current_build == first_build_for_movie.get(movie))

            # Build entry information
            if is_first_build:
                continuous_bars[movie].append({
                    'build': current_build,
                    'type': 'first'
                })
            elif not has_in_current and prev_build:
                reference_data = movie_reference_builds[movie].get(current_build, {'build': None, 'frames': []})
                reference_build = reference_data['build']

                if reference_build:
                    next_build = find_next_appearance(current_build)
                    continuous_bars[movie].append({
                        'build': current_build,
                        'reference_build': reference_build,
                        'type': 'diff',
                        'has_diff': False,
                        'is_skipped': True,
                        'compare_with': reference_build,
                        'next_appearance': next_build
                    })
                else:
                    continuous_bars[movie].append({
                        'build': current_build,
                        'type': 'missing'
                    })
            elif has_in_current and prev_build:
                if has_in_prev:
                    common_frames = set(current_frames).intersection(set(prev_frames))

                    if len(current_frames) < len(prev_frames):
                        has_any_diff = False
                        for frame in common_frames:
                            diff_result = get_image_diff(current_build, prev_build, movie, frame)
                            if diff_result.get('has_diff', False):
                                has_any_diff = True
                                break

                        continuous_bars[movie].append({
                            'build': current_build,
                            'has_diff': has_any_diff,
                            'compare_with': prev_build,
                            'type': 'diff',
                            'is_partial': True
                        })
                    else:
                        has_diff = get_movie_diff_for_frames(
                            current_build, prev_build, target, movie, list(common_frames))

                        continuous_bars[movie].append({
                            'build': current_build,
                            'has_diff': has_diff,
                            'compare_with': prev_build,
                            'type': 'diff'
                        })
                else:
                    # Movie is in current but not in prev — find global reference
                    reference_data = movie_reference_builds[movie].get(current_build, {'build': None, 'frames': []})
                    reference_build = reference_data['build']
                    comparable_frames = reference_data['frames']

                    has_diff = False
                    if reference_build and comparable_frames:
                        has_diff = get_movie_diff_for_frames(current_build, reference_build, target, movie, comparable_frames)

                    continuous_bars[movie].append({
                        'build': current_build,
                        'type': 'readded',
                        'compare_with': reference_build,
                        'common_frames': comparable_frames,
                        'has_diff': has_diff,
                        'no_reference': reference_build is None
                    })
            elif not prev_build:
                # First page, first entry — no context build available
                if has_in_current:
                    continuous_bars[movie].append({
                        'build': current_build,
                        'type': 'no_prev',
                    })
                else:
                    # Check if movie ever appeared in a previous build globally
                    reference_data = movie_reference_builds[movie].get(current_build, {'build': None, 'frames': []})
                    reference_build = reference_data['build']
                    if reference_build:
                        next_build = find_next_appearance(current_build)
                        continuous_bars[movie].append({
                            'build': current_build,
                            'reference_build': reference_build,
                            'type': 'diff',
                            'has_diff': False,
                            'is_skipped': True,
                            'compare_with': reference_build,
                            'next_appearance': next_build
                        })
                    else:
                        continuous_bars[movie].append({
                            'build': current_build,
                            'type': 'missing'
                        })

    # continuous_bars is now already built with display_builds in the correct order
    # Generate URL templates needed by frontend
    urls = {
        'movie_url': url_for('movie', movie='MOVIE_PLACEHOLDER'),
        'compare_url': url_for('compare',
                               build1='BUILD1_PLACEHOLDER',
                               build2='BUILD2_PLACEHOLDER',
                               target='TARGET_PLACEHOLDER',
                               movie='MOVIE_PLACEHOLDER'),
        'single_build_url': url_for('view_single_build',
                                    build='BUILD_PLACEHOLDER',
                                    target='TARGET_PLACEHOLDER',
                                    movie='MOVIE_PLACEHOLDER')
    }

    # Return all data to frontend
    data = {
        'target': target,
        'builds': current_page_builds,
        'movies': movies,
        'display_movies': [decode_string(m) for m in movies],
        'continuous_bars': continuous_bars,
        'urls': urls
    }
    save_target_cache(target, page, data)
    return jsonify(data)

@app.route('/movie/<movie>')
def movie(movie):
    target_builds = {}
    all_builds = set()
    diff_matrix = {}

    # Scan through all targets
    for target in os.listdir(SCREENSHOTS_DIR):
        target_path = os.path.join(SCREENSHOTS_DIR, target)
        if os.path.isdir(target_path):
            # Get sorted builds
            builds = get_sorted_builds(target_path,reverse=False)

            # Find builds containing this movie
            builds_with_movie = []
            for build in builds:
                build_path = os.path.join(target_path, build)
                movie_files = get_movie_frames(build_path, movie)

                if movie_files:
                    builds_with_movie.append(build)
                    all_builds.add(build)

            # Calculate diffs between consecutive builds
            for i in range(1,len(builds_with_movie)):
                current_build = builds_with_movie[i]
                prev_build = builds_with_movie[i - 1]

                has_diff = movie_diff(current_build, prev_build, target, movie)

                if target not in diff_matrix:
                    diff_matrix[target] = {}

                diff_matrix[target][(current_build, prev_build)] = has_diff

            if builds_with_movie:
                target_builds[target] = builds_with_movie

    all_builds = sorted(list(all_builds), reverse=False)

    return render_template('movie.html',
                           movie=movie,
                           display_movie=decode_string(movie),
                           target_builds=target_builds,
                           all_builds=all_builds,
                           diff_matrix=diff_matrix)

@app.route('/build/<build>')
def build(build):
    target_info = {}

    for target in os.listdir(SCREENSHOTS_DIR):
        target_path = os.path.join(SCREENSHOTS_DIR, target)
        if not os.path.isdir(target_path):
            continue

        # Get sorted builds
        builds = get_sorted_builds(target_path,reverse=False)

        # Check if current build exists in this target
        if build not in builds:
            continue

        # Find the previous build
        build_index = builds.index(build)
        prev_build = builds[build_index - 1] if build_index > 0 else None

        # Find all movies in this build
        build_path = os.path.join(target_path, build)
        movie_files = get_movie_frames(build_path)
        movies = extract_movie_names(movie_files)

        # Calculate differences for each movie
        movie_diffs = {}
        if prev_build:
            for movie in movies:
                has_diff = movie_diff(build, prev_build, target, movie)
                movie_diffs[movie] = has_diff

        # Store target information
        target_info[target] = {
            'prev_build': prev_build,
            'movies': sorted(list(movies)),
            'movie_diffs': movie_diffs
        }

    return render_template('build.html',
                           build=build,
                           target_info=target_info)

@app.route('/compare/<build1>/<build2>/<target>/<movie>')
def compare(build1, build2, target, movie):
    build1_path = os.path.join(SCREENSHOTS_DIR, target, build1)
    build2_path = os.path.join(SCREENSHOTS_DIR, target, build2)

    # Get all frames for this movie in both builds
    build1_frames = get_movie_frames(build1_path, movie)
    build2_frames = get_movie_frames(build2_path, movie)

    # Map frame numbers to filenames for easy lookup
    build1_frame_map = create_frame_map(build1_frames)
    build2_frame_map = create_frame_map(build2_frames)

    # Find only common frames between the two builds
    common_frame_numbers = sorted(set(build1_frame_map.keys()).intersection(set(build2_frame_map.keys())))

    # For each common frame number, create a comparison entry
    frame_comparisons = []

    # Process only common frames
    for frame_num in common_frame_numbers:
        build1_frame = build1_frame_map.get(frame_num)
        build2_frame = build2_frame_map.get(frame_num)

        comparison = {
            'frame_number': frame_num,
            'build1_frame': build1_frame,
            'build2_frame': build2_frame,
            'has_diff': False,
            'diff_data': None
        }

        # Calculate diff
        img1_path = os.path.join(build1_path, build1_frame)
        img2_path = os.path.join(build2_path, build2_frame)

        try:
            diff_result = image_diff(img1_path, img2_path)
            comparison['has_diff'] = diff_result.get('has_diff', False)
            comparison['diff_data'] = diff_result
        except Exception as e:
            print(f"Error comparing images: {e}")

        frame_comparisons.append(comparison)

    # Calculate summary statistics
    stats = {
        'total_common_frames': len(common_frame_numbers),
        'different_frames': sum(1 for comp in frame_comparisons if comp.get('has_diff', False))
    }

    return render_template('compare.html',
                           build1=build1,
                           build2=build2,
                           target=target,
                           movie=movie,
                           comparisons=frame_comparisons,
                           stats=stats)

@app.route('/view/<target>/<build>/<movie>')
def view_single_build(target, build, movie):
    """
    Display all frames of a movie from a single build without comparison.
    """
    build_path = os.path.join(SCREENSHOTS_DIR, target, build)
    frames = get_movie_frames(build_path, movie)

    # Prepare frame data for the template
    frame_data = []
    for frame in frames:
        frame_path = os.path.join(build_path, frame)
        frame_num = get_frame_number(frame)

        try:
            img = Image.open(frame_path)
            img_data = encode_image(img)

            frame_data.append({
                'frame_number': frame_num,
                'filename': frame,
                'img_data': img_data
            })
        except Exception as e:
            print(f"Error processing frame {frame}: {e}")

    return render_template('view.html',
                           target=target,
                           build=build,
                           movie=movie,
                           frames=frame_data)

@app.route('/screenshots/<path:filename>')
def screenshots(filename):
    return send_from_directory(SCREENSHOTS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', port=5002)
