#!/usr/bin/env python

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

import argparse
import subprocess
import tempfile

from typing import Optional

__all__ = [
    "BCFExtrasInputError",
    "copy_compress_index",
    "add_header_lines",
]


class BCFExtrasInputError(Exception):
    pass


def copy_compress_index(vcf):
    vcf_gz = f"{vcf}.gz"
    subprocess.check_call(["bcftools", "sort", "-o", vcf_gz, "-O" "z", vcf])
    subprocess.check_call(["tabix", "-f", "-p", "vcf", vcf_gz])


def add_header_lines(
        vcf: str,
        lines,
        start: Optional[int] = None,
        end: Optional[int] = None,
        tmp_dir: Optional[str] = None,
        delete_old: bool = True):
    if start is None and end is None:
        end = 0

    if start is not None and end is not None:
        raise BCFExtrasInputError("add_header_lines: Cannot set both start and end offsets")

    header = [
        line.strip()
        for line in subprocess.check_output(["bcftools", "view", "-h", vcf]).split(b"\n")
        if not line.startswith(b"##bcftools")  # get rid of extra bcftools junk
    ]
    incl_length = len(header) - 2  # Exclude first and last lines (fileformat/CHROM etc respectively)

    with open(lines, "rb") as lf:
        new_lines = [line.strip() for line in lf.readlines() if line.strip()]

    # ##fileformat
    # 0
    # ## other
    # 1
    # #CHROM ...
    if start is not None and start > incl_length:
        raise BCFExtrasInputError(f"add_header_lines: Start offset is past last header ({start} > {incl_length})")

    # Reverso!
    # #CHROM
    # 0
    # ## other
    # 1
    # ##fileformat
    if end is not None and end > incl_length:
        raise BCFExtrasInputError(f"add_header_lines: End offset is past first header ({end} > {incl_length})")

    if end is not None:
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

        # Re-header the VCF file
        new_fn = f"{vcf}.new"
        old_fn = f"{vcf}.old"
        subprocess.check_call(["bcftools", "reheader", "-h", tmpfile.name, "-o", new_fn, vcf])
        subprocess.check_call(["mv", vcf, old_fn])
        subprocess.check_call(["mv", new_fn, vcf])

        if delete_old:
            subprocess.check_call(["rm", old_fn])


ACTION_COPY_COMPRESS_INDEX = "copy-compress-index"
ACTION_ADD_HEADER_LINES = "add-header-lines"


def main():
    parser = argparse.ArgumentParser(
        description="A set of variant file helper utilities built on top of bcftools and htslib.")
    subparsers = parser.add_subparsers(
        dest="action",
        title="action",
        help="The action to run. Each action has its own set of arguments.",
        required=True)

    cci_parser = subparsers.add_parser(
        ACTION_COPY_COMPRESS_INDEX,
        help="Compresses a VCF to a bgzipped copy with a tabix index, leaving the original intact.")
    cci_parser.add_argument("vcf", type=str, help="The VCF to process.")

    ahl_parser = subparsers.add_parser(
        ACTION_ADD_HEADER_LINES,
        help="Inserts new VCF header lines from stdin to either the end of the header (default) or to a specified "
             "position in a VCF file, in-place. Ignores the first and last header lines (fileformat/#CHROM.)")
    ahl_parser.add_argument("vcf", type=str, help="The VCF to process.")
    ahl_parser.add_argument("lines", type=str, help="The text file with header lines to insert.")
    ahl_parser.add_argument(
        "--tmp-dir",
        type=str,
        default=None,
        help="Temporary directory path for VCF header artifacts.")
    ahl_parser.add_argument(
        "--start",
        type=int,
        default=None,
        help="0-indexed offset from the start of the header, excluding fileformat line (e.g. --start 0 will insert "
             "right after ##fileformat.)")
    ahl_parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="0-indexed offset from the start of the header, excluding fileformat line (e.g. --end 0 will insert "
             "right before #CHROM.)")
    ahl_parser.add_argument(
        "--keep-old",
        action="store_true",
        help="Whether to keep the original file (as {filename}.old) post-header-change. Off by default.")

    args = parser.parse_args()

    # TODO: py3.10: match
    if args.action == ACTION_COPY_COMPRESS_INDEX:
        copy_compress_index(args.vcf)
    elif args.action == ACTION_ADD_HEADER_LINES:
        add_header_lines(args.vcf, args.lines, args.start, args.end, delete_old=not args.keep_old)


if __name__ == "__main__":
    main()
