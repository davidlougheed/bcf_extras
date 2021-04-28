import os

from bcf_extras.entry import add_header_lines


f = os.path.join(os.path.dirname(__file__), "vcfs", "ahl.vcf")
f_old = f"{f}.old"
lf = os.path.join(os.path.dirname(__file__), "vcfs", "new_lines.txt")

t1 = os.path.join(os.path.dirname(__file__), "vcfs", "ahl_target_1.vcf")
t2 = os.path.join(os.path.dirname(__file__), "vcfs", "ahl_target_2.vcf")
t3 = os.path.join(os.path.dirname(__file__), "vcfs", "ahl_target_3.vcf")


def test_add_header_lines_1_a():
    add_header_lines(vcf=f, lines=lf, start=0, delete_old=False)

    try:
        with open(f, "r") as nf, open(t1, "r") as tf:
            assert nf.read() == tf.read()
    finally:  # Reset everything
        os.remove(f)
        os.rename(f_old, f)


def test_add_header_lines_1_b():
    add_header_lines(vcf=f, lines=lf, end=3, delete_old=False)

    try:
        with open(f, "r") as nf, open(t1, "r") as tf:
            assert nf.read() == tf.read()
    finally:  # Reset everything
        os.remove(f)
        os.rename(f_old, f)


# TODO: Insertion in middle
# TODO: Error raising
