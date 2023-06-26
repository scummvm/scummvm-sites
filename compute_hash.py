import hashlib
import os
import argparse


def filesize(filepath):
    """ Returns size of file """
    return os.stat(filepath).st_size


def checksum(filepath, alg, size):
    """ Returns checksum value of file using a specific algoritm """
    with open(filepath, "rb") as file:
        # Will contain 5 elements:
        #  - Full size checksum
        #  - Checksum of first 5000B
        #  - Checksum of first 1MB
        #  - Checksum of last 5000B (tail)
        #  - Checksum of first *size* bytes
        hashes = []

        if alg == "md5":
            hashes = [hashlib.md5() for _ in range(5)]
        elif alg == "sha1":
            hashes = [hashlib.sha1() for _ in range(5)]
        elif alg == "sha256":
            hashes = [hashlib.sha256() for _ in range(5)]

        # Read file in 8MB chunks for full checksum
        for byte_block in iter(lambda: file.read(8 * 1024 * 1024), b""):
            hashes[0].update(byte_block)

        # First 5000B
        file.seek(0)
        hashes[1].update(file.read(5000))

        # First 1MB
        file.seek(0)
        hashes[2].update(file.read(1024 * 1024))

        # Last 5000B
        if filesize(filepath) >= 5000:
            file.seek(-5000, os.SEEK_END)
            hashes[3].update(file.read())
        else:
            hashes[3] = hashes[0]

        # Custom size; may be None
        # Size is in bytes
        # Reads entire required size at once, inefficient for large sizes
        if size and size <= filesize(filepath):
            file.seek(0)
            hashes[4].update(file.read(size))
        else:
            hashes[4] = None

        hashes = [h.hexdigest() for h in hashes if h]
        hashes[3] = 't:' + hashes[3]  # Add tail prefix
        return hashes


def compute_hash_of_dir(directory, depth, alg="md5", size=0):
    """ Return dictionary containing checksums of all files in directory """
    res = dict()
    # Getting contents of directory and filtering only the files
    files = [f for f in os.listdir(directory) if os.path.isfile(
        os.path.join(directory, f))]

    for file in files:
        res[file] = checksum(os.path.join(directory, file), alg=alg, size=size)

    return res


def create_dat_file(hash_of_dir, path):
    with open(f"{os.path.basename(path)}.dat", "w") as file:
        # Header
        file.writelines([
            "scummvm (\n",
            f"\tauthor cli\n",
            ")\n\n"
        ])

        # Game files
        file.write("game (\n")
        for filename, hashes in hash_of_dir.items():
            # Only works for MD5s, ignores optional extra size
            data = f"name \"{filename}\" size {filesize(os.path.join(path, filename))} md5 {hashes[0]} md5-5000 {hashes[1]} md5-1M {hashes[2]} md5-5000-t {hashes[3]}"
            file.write(f"\trom ( {data} )\n")
        file.write(")\n\n")


parser = argparse.ArgumentParser()
parser.add_argument("--directory",
                    help="Path of directory with game files")
parser.add_argument("--depth",
                    help="Depth from root to game directories")
parser.add_argument("--size",
                    help="Use first n bytes of file to calculate checksum")
args = parser.parse_args()
path = os.path.abspath(args.directory) if args.directory else os.getcwd()
depth = args.depth
checksum_size = args.size


path = os.path.expanduser("~/Downloads/drascula-1.0")
create_dat_file(compute_hash_of_dir(path, depth, size=4000), path)
