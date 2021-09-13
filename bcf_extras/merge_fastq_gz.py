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

import subprocess

from typing import List

__all__ = [
    "merge_fastq_gz",
]


def merge_fastq_gz(files: List[str], out_file: str):
    output_compressed = out_file.endswith(".gz")
    out_path = out_file.rstrip(".gz")

    with open(out_path, "w") as fh:
        for file in files:
            if file.endswith(".gz"):
                subprocess.run(["bgzip", "-d", "-c", file], stdout=fh)
            else:
                subprocess.run(["cat", file], stdout=fh)

    if output_compressed:
        subprocess.run(["bgzip", out_path])
