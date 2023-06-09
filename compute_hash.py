import hashlib
import zlib
import os


def filesize(filepath):
    """ Returns size of file """
    return os.stat(filepath).st_size


def checksum(filepath, alg, size):
    """ Returns checksum value of file using a specific algoritm """
    with open(filepath, "rb") as file:
        if alg == "md5":
            md5_hash = hashlib.md5()
            # Read file in 8MB chunks
            for byte_block in iter(lambda: file.read(8388608), b""):
                md5_hash.update(byte_block)
            return md5_hash.hexdigest()

        elif alg == "crc32":
            crc_hash = 0
            for byte_block in iter(lambda: file.read(8388608), b""):
                crc_hash += zlib.crc32(byte_block)
                crc_hash &= 0xffffffff  # Keeping it at 32 bits
            return crc_hash

        elif alg == "sha1":
            sha1_hash = hashlib.sha1()
            for byte_block in iter(lambda: file.read(8388608), b""):
                sha1_hash.update(byte_block)
            return sha1_hash.hexdigest()

        elif alg == "sha256":
            sha256_hash = hashlib.sha256()
            for byte_block in iter(lambda: file.read(8388608), b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()


def compute_hash_of_dir(directory, alg="md5", size=0):
    """ Return dictionary containing checksums of all files in directory """
    res = dict()
    # Getting contents of directory and filtering only the files
    files = [f for f in os.listdir(directory) if os.path.isfile(
        os.path.join(directory, f))]

    for file in files:
        res[file] = checksum(os.path.join(directory, file), alg=alg, size=size)

    return res


path = os.path.expanduser("~/test")
print(compute_hash_of_dir(path, alg="sha256"))
