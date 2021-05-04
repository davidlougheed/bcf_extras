# bcf_extras is a set of variant file helper utilities built on top of bcftools and htslib.
# Copyright (C) 2021  David Lougheed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import subprocess
import tempfile

from typing import Optional

from .exceptions import BCFExtrasInputError


def add_header_lines(
        vcf: str,
        lines: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        tmp_dir: Optional[str] = None,
        delete_old: bool = False):
    """
    Utility to insert header lines from a text file into a VCF.
    :param vcf: The VCF to add header lines to.
    :param lines: The text file containing the lines in question.
    :param start: 0-indexed offset from the start of the header, excluding fileformat line.
    :param end: 0-indexed offset from the start of the header, excluding #CHROM line.
    :param tmp_dir: Optionally, a directory to put header file fragments during processing.
    :param delete_old: Whether to delete the original VCF or keep it with a .old file extension.
    """

    if start is None and end is None:
        end = 0

    if start is not None and end is not None:
        raise BCFExtrasInputError("add_header_lines: Cannot set both start and end offsets")

    header = [
        line.strip()
        for line in subprocess.check_output(["bcftools", "view", "-h", vcf]).split(b"\n")
        if not line.startswith(b"##bcftools")  # get rid of extra bcftools junk
        if line.strip()
    ]
    incl_length = len(header) - 2  # Exclude first and last lines (fileformat/CHROM etc respectively)

    with open(lines, "rb") as lf:
        new_lines = [line.strip() for line in lf.readlines() if line.strip()]

    # ##fileformat
    # 0
    # ## other
    # 1
    # #CHROM ...
    if start is not None:
        if start < 0:
            raise BCFExtrasInputError(f"add_header_lines: Start offset cannot be negative")
        elif start > incl_length:
            raise BCFExtrasInputError(f"add_header_lines: Start offset is past last header ({start} > {incl_length})")

    # Reverso!
    # #CHROM
    # 0
    # ## other
    # 1
    # ##fileformat
    if end is not None:
        if end < 0:
            raise BCFExtrasInputError(f"add_header_lines: End offset cannot be negative")
        elif end > incl_length:
            raise BCFExtrasInputError(f"add_header_lines: End offset is past first header ({end} > {incl_length})")

        # Reverse lines to have consistent indexing strategy
        header.reverse()
        new_lines.reverse()

    offset = start if start is not None else end

    # Need to offset by one because we didn't include the peripheral two lines
    header = header[:offset+1] + new_lines + header[offset+1:]

    if end is not None:
        # Un-reverse
        header.reverse()

    tmp_dir = tmp_dir or "/tmp"
    with tempfile.NamedTemporaryFile(dir=tmp_dir) as tmpfile:
        tmpfile.write(b"\n".join(header) + b"\n")
        tmpfile.flush()

        # Re-header the VCF file
        new_fn = f"{vcf}.new"
        old_fn = f"{vcf}.old"
        subprocess.check_call(["bcftools", "reheader", "-h", tmpfile.name, "-o", new_fn, vcf])
        os.rename(vcf, old_fn)
        os.rename(new_fn, vcf)

        if delete_old:
            os.remove(old_fn)
