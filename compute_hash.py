import hashlib
import os
import argparse
import struct
import zlib

script_version = "0.1"


def filesize(filepath):
    """ Returns size of file """
    return os.stat(filepath).st_size


def get_dirs_at_depth(directory, depth):
    directory = directory.rstrip(os.path.sep)
    assert os.path.isdir(directory)
    num_sep = directory.count(os.path.sep)

    for root, dirs, contents in os.walk(directory):
        num_sep_this = root.count(os.path.sep)
        if depth == num_sep_this - num_sep:
            yield root


def read_be(byte_stream, size_in_bits):
    """ Return unsigned integer of size_in_bits, assuming the data is big-endian """
    (uint,) = struct.unpack(">I", byte_stream[:size_in_bits//8])
    return uint


def is_macbin(filepath):
    with open(filepath, "rb") as file:
        header = file.read(128)
        if len(header) != 128:
            return False

        res_fork_offset = -1

        # Preliminary check
        # Exclude files that have zero name len, zero data fork, zero name fork and zero type_creator.
        if not header[1] and not read_be(header[83:], 32) and not read_be(header[87:], 32) and not read_be(header[69:], 32):
            return False

        checksum = zlib.crc32(header)
        if checksum != read_be(header[124:], 32):
            return False

        if not header[0] and not header[74] and not header[82] and header[1] <= 63:
            # Get fork lengths
            datalen = read_be(header[83:], 32)
            rsrclen = read_be(header[87:], 32)

            # Files produced by ISOBuster are not padded, thus, compare with the actual size
            datalen_pad = (((datalen + 127) >> 7) << 7)

            # Length check
            if (128 + datalen_pad + rsrclen >= len(header)):
                return False

            return True


def macbin_get_resfork(file_byte_stream):
    if not file_byte_stream:
        return file_byte_stream

    (datalen,) = struct.unpack(">I", file_byte_stream[0x53:0x57])
    return file_byte_stream[0x80 + datalen:]


def macbin_get_datafork(file_byte_stream):
    if not file_byte_stream:
        return file_byte_stream

    (datalen,) = struct.unpack(">I", file_byte_stream[0x53:0x57])
    return file_byte_stream[0x80: 0x80 + datalen]


def create_checksum_pairs(hashes, alg, size, prefix=None):
    res = []

    keys = [f"{alg}", f"{alg}-5000", f"{alg}-1M", f"{alg}-5000-t"]
    if size:
        keys.append(f"{alg}-{size}")
    if prefix:
        keys = [key+f'-{prefix}' for key in keys]

    for i, h in enumerate(hashes):
        res.append((keys[i], h))

    return res


def file_checksum(filepath, alg, size):
    if not is_macbin(filepath):
        with open(filepath, "rb") as file:
            return create_checksum_pairs(checksum(file, alg, size, filepath), alg, size)

            # If the file is a MacBinary
    with open(filepath, "rb") as file:
        res = []

        file = macbin_get_resfork(file.read())
        prefix = 'r'

        if len(file):
            for h in checksum(file, alg, size, filepath):
                if ':' not in h:
                    res.append(f"{prefix}:{h}")
                else:
                    # If the checksum is like "t:..."
                    res.append(f"{prefix}{h}")

        file = macbin_get_datafork(file)
        prefix = 'd'

        for h in checksum(file, alg, size, filepath):
            if ':' not in h:
                res.append(f"{prefix}:{h}")
            else:
                res.append(f"{prefix}{h}")  # If the checksum is like "t:..."

        return create_checksum_pairs(res, alg, size, prefix)


def checksum(file, alg, size, filepath):
    """ Returns checksum value of file buffer using a specific algoritm """
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

    # If file is not a MacBinary
    if not isinstance(file, bytes):
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
    else:
        bytes_stream = file

        hashes[0].update(bytes_stream)
        hashes[1].update(bytes_stream[:5000])
        hashes[2].update(bytes_stream[:1024 * 1024])
        if filesize(filepath) >= 5000:
            hashes[3].update(bytes_stream[-5000:])
        else:
            hashes[3] = hashes[0]

        # Custom size
        if size and size <= filesize(filepath):
            hashes[4].update(bytes_stream[:size])
        else:
            hashes[4] = None

    hashes = [h.hexdigest() for h in hashes if h]
    hashes[3] = 't:' + hashes[3]  # Add tail prefix
    return hashes


def compute_hash_of_dirs(root_directory, depth, size=0, alg="md5"):
    """ Return dictionary containing checksums of all files in directory """
    res = []

    for directory in get_dirs_at_depth(root_directory, depth):
        hash_of_dir = dict()
        files = []

        # Getting only files of directory and subdirectories recursively
        for root, dirs, contents in os.walk(directory):
            files.extend([os.path.join(root, f) for f in contents])

        for file in files:
            hash_of_dir[os.path.relpath(file, directory)] = (file_checksum(
                file, alg, size), filesize(file))

        res.append(hash_of_dir)

    return res


def create_dat_file(hash_of_dirs, path, checksum_size=0):
    with open(f"{os.path.basename(path)}.dat", "w") as file:
        # Header
        file.writelines([
            "scummvm (\n",
            f"\tauthor scan\n",
            f"\tversion {script_version}\n",
            ")\n\n"
        ])

        # Game files
        for hash_of_dir in hash_of_dirs:
            file.write("game (\n")
            for filename, (hashes, filesize) in hash_of_dir.items():
                data = f"name \"{filename}\" size {filesize}"
                for key, value in hashes:
                    data += f" {key} {value}"

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
depth = int(args.depth) if args.depth else 0
checksum_size = int(args.size) if args.size else 0

create_dat_file(compute_hash_of_dirs(
    path, depth, checksum_size), path, checksum_size)
