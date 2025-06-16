from db_functions import punycode_need_encode, encode_punycode


def test_needs_punyencoding():
    checks = [
        ["Icon\r", True],
        ["ascii", False],
        ["ends with dot .", True],
        ["ends with space ", True],
        ["バッドデイ(Power PC)", True],
        ["Hello*", True],
        ["File I/O", True],
        ["HDにｺﾋﾟｰして下さい。G3", True],
        ["Buried in Time™ Demo", True],
        ["•Main Menu", True],
        ["Spaceship Warlock™", True],
        ["ワロビージャックの大冒険<デモ>", True],
        ["Jönssonligan går på djupet.exe", True],
        ["Jönssonligan.exe", True],
        ["G3フォルダ", True],
        ["Big[test]", False],
        [
            'Where \\ Do <you> Want / To: G* ? ;Unless=nowhere,or|"(everything)/":*|\\?%<>,;=',
            True,
        ],
        ["Buried in Timeｪ Demo", True],
    ]
    for input, expected in checks:
        assert punycode_need_encode(input) == expected


def test_punycode_encode():
    checks = [
        ["Icon\r", "xn--Icon-ja6e"],
        ["ascii", "ascii"],
        ["ends with dot .", "xn--ends with dot .-"],
        ["ends with space ", "xn--ends with space -"],
        ["バッドデイ(Power PC)", "xn--(Power PC)-jx4ilmwb1a7h"],
        ["Hello*", "xn--Hello-la10a"],
        ["File I/O", "xn--File IO-oa82b"],
        ["HDにｺﾋﾟｰして下さい。G3", "xn--HDG3-rw3c5o2dpa9kzb2170dd4tzyda5j4k"],
        ["Buried in Time™ Demo", "xn--Buried in Time Demo-eo0l"],
        ["•Main Menu", "xn--Main Menu-zd0e"],
        ["Spaceship Warlock™", "xn--Spaceship Warlock-306j"],
        [
            "ワロビージャックの大冒険<デモ>",
            "xn--baa0pja0512dela6bueub9gshf1k1a1rt742c060a2x4u",
        ],
        ["Jönssonligan går på djupet.exe", "xn--Jnssonligan gr p djupet.exe-glcd70c"],
        ["Jönssonligan.exe", "xn--Jnssonligan.exe-8sb"],
        ["G3フォルダ", "xn--G3-3g4axdtexf"],
        ["Big[test]", "Big[test]"],
        [
            'Where \\ Do <you> Want / To: G* ? ;Unless=nowhere,or|"(everything)/":*|\\?%<>,;=',
            "xn--Where  Do you Want  To G  ;Unless=nowhere,or(everything),;=-5baedgdcbtamaaaaaaaaa99woa3wnnmb82aqb71ekb9g3c1f1cyb7bx6rfcv2pxa",
        ],
        ["Buried in Timeｪ Demo", "xn--Buried in Time Demo-yp97h"],
    ]
    for input, expected in checks:
        assert encode_punycode(input) == expected
