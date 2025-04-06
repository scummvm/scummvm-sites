import os

from PIL import Image
from flask import Flask, render_template, jsonify, url_for, send_from_directory

from config import SCREENSHOTS_DIR
from imagediff import image_diff, encode_image, movie_diff

app = Flask(__name__)

def get_frame_number(filename):
    """Extract frame number from filename."""
    parts = filename.split('-')
    if len(parts) > 1:
        try:
            return int(parts[1].split('.')[0])
        except ValueError:
            return 0
    return 0

def get_sorted_builds(target_path, reverse=True):
    """Get sorted list of builds for a target."""
    builds = [b for b in os.listdir(target_path)
              if os.path.isdir(os.path.join(target_path, b))]
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

            if "-" in file:
                parts = file.split("-")
                movie_name = parts[0]
                frame_num = parts[1].split('.')[0]

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
            movie_name = file.split("-")[0]
            movies.add(movie_name)
    return movies

def create_frame_map(frames):
    """Create a map of frame numbers to filenames."""
    return {get_frame_number(f): f for f in frames}

@app.route('/')
def index():
    targets = [d for d in os.listdir(SCREENSHOTS_DIR)
               if os.path.isdir(os.path.join(SCREENSHOTS_DIR, d))]

    return render_template('index.html', targets=targets)

@app.route('/target/<target>')
def target_detail(target):
    target_path = os.path.join(SCREENSHOTS_DIR, target)

    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        return "Target not found", 404

    # Only get the build list, other time-consuming operations moved to API
    builds = get_sorted_builds(target_path)

    # Only return the page framework with build list but without table data
    return render_template('target.html',
                           target=target,
                           builds=builds)

# Handle time-consuming data calculations
@app.route('/api/target_data/<target>')
def target_data_api(target):
    target_path = os.path.join(SCREENSHOTS_DIR, target)

    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        return jsonify({"error": "Target not found"}), 404

    builds = get_sorted_builds(target_path)
    builds_ascending = get_sorted_builds(target_path, reverse=False)

    # Collect movie frame data
    all_movies, build_movie_frames, _ = collect_movie_frames(target_path, builds)

    # Calculate first build for each movie
    first_build_for_movie = find_first_build_for_movies(
        all_movies, builds_ascending, build_movie_frames)

    # Calculate reference builds
    movie_reference_builds = {}
    for movie in all_movies:
        movie_reference_builds[movie] = {}
        for i, current_build in enumerate(builds):
            has_in_current = movie in build_movie_frames.get(current_build, {})
            current_frames = build_movie_frames.get(current_build, {}).get(movie, [])

            if not has_in_current:
                # Reference build needs to have the movie
                reference_build = None
                for j in range(i+1, len(builds)):
                    next_build = builds[j]
                    if movie in build_movie_frames.get(next_build, {}):
                        reference_build = next_build
                        break
                movie_reference_builds[movie][current_build] = {
                    'build': reference_build,
                    'frames': []  # Empty since current build doesn't have the movie
                }
            else:
                # Current build has the movie, find a reference build with matching frames
                reference_data = {
                    'build': None,
                    'frames': current_frames
                }

                for j in range(i+1, len(builds)):
                    next_build = builds[j]
                    if movie in build_movie_frames.get(next_build, {}):
                        next_frames = build_movie_frames.get(next_build, {}).get(movie, [])

                        # Check if current frames exist in the next build
                        common_frames = set(current_frames).intersection(set(next_frames))
                        if common_frames:
                            reference_data = {
                                'build': next_build,
                                'frames': list(common_frames)
                            }
                            break

                movie_reference_builds[movie][current_build] = reference_data

    # Pre-calculate image difference results
    image_diff_cache = {}
    def get_image_diff(current_build, prev_build, movie, frame):
        cache_key = (current_build, prev_build, movie, frame)
        if cache_key not in image_diff_cache:
            current_frame_path = os.path.join(target_path, current_build, f"{movie}-{frame}.png")
            prev_frame_path = os.path.join(target_path, prev_build, f"{movie}-{frame}.png")

            if os.path.exists(current_frame_path) and os.path.exists(prev_frame_path):
                try:
                    image_diff_cache[cache_key] = image_diff(current_frame_path, prev_frame_path)
                except Exception as e:
                    print(f"Error comparing frames {movie}-{frame}: {e}")
                    image_diff_cache[cache_key] = {'has_diff': True}
            else:
                image_diff_cache[cache_key] = {'has_diff': True}

        return image_diff_cache[cache_key]

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
    movie_diff_cache = {}
    def get_movie_diff_cached(current_build, prev_build, target, movie):
        cache_key = (current_build, prev_build, target, movie)
        if cache_key not in movie_diff_cache:
            movie_diff_cache[cache_key] = movie_diff(current_build, prev_build, target, movie)
        return movie_diff_cache[cache_key]

    movies = sorted(list(all_movies))
    continuous_bars = {}

    # Create continuous bars for visualization with updated skip logic
    for movie in movies:
        continuous_bars[movie] = []

        for i, current_build in enumerate(builds):
            prev_build = builds[i+1] if i < len(builds)-1 else None

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
                # Modified skip build logic
                reference_data = movie_reference_builds[movie].get(current_build, {'build': None, 'frames': []})
                reference_build = reference_data['build']

                if reference_build:
                    continuous_bars[movie].append({
                        'build': current_build,
                        'reference_build': reference_build,
                        'type': 'diff',
                        'has_diff': False,  # No diff since current build doesn't have the movie
                        'is_skipped': True,
                        'compare_with': reference_build
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
                        # End difference check loop early
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
                        has_diff = get_movie_diff_cached(current_build, prev_build, target, movie)

                        continuous_bars[movie].append({
                            'build': current_build,
                            'has_diff': has_diff,
                            'compare_with': prev_build,
                            'type': 'diff'
                        })
                else:
                    # Modified readded build logic
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
                continuous_bars[movie].append({
                    'build': current_build,
                    'type': 'unknown'
                })

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
        'builds': builds,
        'movies': movies,
        'continuous_bars': continuous_bars,
        'urls': urls
    }

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
            builds = get_sorted_builds(target_path)

            # Find builds containing this movie
            builds_with_movie = []
            for build in builds:
                build_path = os.path.join(target_path, build)
                movie_files = get_movie_frames(build_path, movie)

                if movie_files:
                    builds_with_movie.append(build)
                    all_builds.add(build)

            # Calculate diffs between consecutive builds
            for i in range(len(builds_with_movie) - 1):
                current_build = builds_with_movie[i]
                prev_build = builds_with_movie[i + 1]

                has_diff = movie_diff(current_build, prev_build, target, movie)

                if target not in diff_matrix:
                    diff_matrix[target] = {}

                diff_matrix[target][(current_build, prev_build)] = has_diff

            if builds_with_movie:
                target_builds[target] = builds_with_movie

    all_builds = sorted(list(all_builds), reverse=True)

    return render_template('movie.html',
                           movie=movie,
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
        builds = get_sorted_builds(target_path)

        # Check if current build exists in this target
        if build not in builds:
            continue

        # Find the previous build
        build_index = builds.index(build)
        prev_build = builds[build_index + 1] if build_index < len(builds) - 1 else None

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
    app.run(debug=True, port=5001)