import os

import pytest

from bcf_extras.add_header_lines import add_header_lines
from bcf_extras.entry import main
from bcf_extras.exceptions import BCFExtrasInputError


f = os.path.join(os.path.dirname(__file__), "vcfs", "ahl.vcf")
f_old = f"{f}.old"
lf = os.path.join(os.path.dirname(__file__), "vcfs", "new_lines.txt")

t1 = os.path.join(os.path.dirname(__file__), "vcfs", "ahl_target_1.vcf")
t2 = os.path.join(os.path.dirname(__file__), "vcfs", "ahl_target_2.vcf")
t3 = os.path.join(os.path.dirname(__file__), "vcfs", "ahl_target_3.vcf")


def _test_add_header_lines(target, **kwargs):
    add_header_lines(vcf=f, lines=lf, delete_old=False, **kwargs)

    try:
        with open(f, "r") as nf, open(target, "r") as tf:
            assert nf.read() == tf.read()
    finally:  # Reset everything
        os.remove(f)
        os.rename(f_old, f)


def test_add_header_lines_1_a():
    _test_add_header_lines(t1, start=0)


def test_add_header_lines_1_b():
    _test_add_header_lines(t1, end=3)


def test_add_header_lines_2_a():
    _test_add_header_lines(t2, start=3)


def test_add_header_lines_2_b():
    _test_add_header_lines(t2, end=0)


def test_add_header_lines_3_a():
    _test_add_header_lines(t3, start=1)


def test_add_header_lines_3_b():
    _test_add_header_lines(t3, end=2)


def test_add_header_lines_raises_1():
    with pytest.raises(BCFExtrasInputError):
        add_header_lines(vcf=f, lines=lf, delete_old=False, start=-1)

    with pytest.raises(BCFExtrasInputError):
        add_header_lines(vcf=f, lines=lf, delete_old=False, start=4)


def test_add_header_lines_raises_2():
    with pytest.raises(BCFExtrasInputError):
        add_header_lines(vcf=f, lines=lf, delete_old=False, end=-1)

    with pytest.raises(BCFExtrasInputError):
        add_header_lines(vcf=f, lines=lf, delete_old=False, end=4)


def test_cli_1():
    main(["add-header-lines", f, lf, "--start", "0"])

    try:
        with open(f, "r") as nf, open(t1, "r") as tf:
            assert nf.read() == tf.read()
    finally:  # Reset everything
        os.remove(f)
        os.rename(f_old, f)


def test_cli_raises():
    with pytest.raises(SystemExit):
        main(["add-header-lines", f, "--start", "0"])
