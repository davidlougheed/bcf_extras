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
    "copy_compress_index",
]


def copy_compress_index(vcfs: List[str]):
    for vcf in vcfs:  # TODO: Parallelize if specified
        vcf_gz = f"{vcf}.gz"
        subprocess.check_call(["bcftools", "sort", "-o", vcf_gz, "-O" "z", vcf])
        subprocess.check_call(["tabix", "-f", "-p", "vcf", vcf_gz])
