import os

from bcf_extras.copy_compress_index import copy_compress_index


def test_cci():
    f = os.path.join(os.path.dirname(__file__), "vcfs", "cci.vcf")

    o1 = os.path.join(os.path.dirname(__file__), "vcfs", "cci.vcf.gz")
    o2 = os.path.join(os.path.dirname(__file__), "vcfs", "cci.vcf.gz.tbi")

    copy_compress_index([f])

    assert os.path.exists(o1)
    assert os.path.exists(o2)

    # Clean up
    os.remove(o1)
    os.remove(o2)
