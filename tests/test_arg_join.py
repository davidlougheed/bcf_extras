import subprocess


def test_arg_join_1():
    s = subprocess.check_output(["python", "-m", "bcf_extras.entry", "arg-join", "f1", "f2"])
    assert s == b"f1,f2"


def test_arg_join_2():
    s = subprocess.check_output(["python", "-m", "bcf_extras.entry", "arg-join", "--sep", ";", "f1", "f2"])
    assert s == b"f1;f2"


def test_arg_join_3():
    s = subprocess.check_output(["python", "-m", "bcf_extras.entry", "arg-join", "--sep", "a"])
    assert s == b""


def test_arg_join_4():
    s = subprocess.check_output(["python", "-m", "bcf_extras.entry", "arg-join", "--sep", "a", "b", "c"])
    assert s == b"bac"
