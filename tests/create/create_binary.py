import struct
import os


def generate_macbinary_test_files():
    output_dir = "../data/invalid_mac_binary/"

    with open(os.path.join(output_dir, "len_less_than_128_bytes.bin"), "wb") as f:
        f.write(b"\x12")

    header = bytearray([1] * 128)
    # name length, data fork len, resource fork len, type/creator
    header[1] = 0
    header[83:87] = struct.pack(">I", 0)
    header[87:91] = struct.pack(">I", 0)
    header[69:73] = struct.pack(">I", 0)

    with open(os.path.join(output_dir, "zero_len_fields.bin"), "wb") as f:
        f.write(header)

    header = bytearray([1] * 128)
    header[1] = 10
    header[124:126] = struct.pack(">H", 0xFFFF)
    with open(os.path.join(output_dir, "bad_checksum.bin"), "wb") as f:
        f.write(header)

    header[124:126] = struct.pack(">H", 4263)
    header[1] = 100
    with open(os.path.join(output_dir, "name_length_too_large.bin"), "wb") as f:
        f.write(header)

    header[1] = 10
    header[83:87] = struct.pack(">I", 100)
    header[87:91] = struct.pack(">I", 50)
    with open(os.path.join(output_dir, "forks_mismatch.bin"), "wb") as f:
        f.write(header)
        f.write(b"\x00" * 50)

    output_dir = "../data/valid_mac_binary/"

    # Valid
    header = bytearray(128)
    header[0] = 0
    header[1] = 5
    header[2:7] = b"test\x00"
    header[69:73] = b"1111"
    header[73:77] = b"1111"
    header[74] = 0
    header[82] = 0
    data_fork_len = 10
    header[83:87] = struct.pack(">I", data_fork_len)
    res_fork_len = 0
    header[87:91] = struct.pack(">I", res_fork_len)
    data_fork = b"0123456789"
    data_fork_len_padded = ((data_fork_len + 127) >> 7) << 7
    data_fork_padded = data_fork + b"\x00" * (data_fork_len_padded - data_fork_len)
    header[124:126] = struct.pack(">H", 27858)

    with open(os.path.join(output_dir, "valid_macbinary.bin"), "wb") as f:
        f.write(header)
        f.write(data_fork_padded)


if __name__ == "__main__":
    generate_macbinary_test_files()
