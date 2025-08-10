import os
from src.scripts.compute_hash import is_macbin


def test_is_macbin():
    invalid_mac_dir = "tests/data/invalid_mac_binary"
    valid_mac_dir = "tests/data/valid_mac_binary"
    checks = []
    for file in os.listdir(valid_mac_dir):
        checks.append([os.path.join(valid_mac_dir, file), True])
    for file in os.listdir(invalid_mac_dir):
        checks.append([os.path.join(invalid_mac_dir, file), False])

    for input, expected in checks:
        assert is_macbin(input) == expected
