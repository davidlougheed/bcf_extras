import math
import multiprocessing
import os
import subprocess

from argparse import Namespace
from datetime import datetime
from typing import List, Optional

from .exceptions import BCFExtrasDependencyError

try:
    from trtools.mergeSTR.mergeSTR import main as mergestr_main
except ModuleNotFoundError:
    mergestr_main = None

__all__ = [
    "parallel_mergestr",
]


def _merge_small_last(vcfs: List[List[str]], group_size: int):
    # If there's a small leftovers group, merge it in with its predecessor (if one exists)
    # Otherwise, keep the list as-is
    return vcfs[:-2] + [vcfs[-2] + vcfs[-1]] if len(vcfs[-1]) < group_size and len(vcfs) > 1 else vcfs


def _merge(
        prefix: str,
        idx: Optional[int],
        vcfs: List[str],
        vcf_type: str,
        level: Optional[int],
        remove_previous: bool
):
    out_file_prefix = f"{prefix}_{level}_{idx}" if level is not None and idx is not None else prefix

    print(f"\tMerging [{', '.join(vcfs)}] to {out_file_prefix}.vcf")

    mergestr_main(Namespace(
        out=out_file_prefix,
        vcfs=",".join(vcfs),
        vcftype=vcf_type,
        update_sample_from_file=False,   # TODO: Pass in
        verbose=False,   # TODO: Pass in
        quiet=False,   # TODO: Pass in
    ))

    if remove_previous:
        for vcf in vcfs:
            os.remove(vcf)

    return f"{out_file_prefix}.vcf"


def _compress(vcf: str):
    subprocess.check_call(["bgzip", vcf])
    gz = f"{vcf}.gz"
    subprocess.check_call(["tabix", "-f", "-p", "vcf", gz])
    return gz


def parallel_mergestr(
        vcfs: List[str],
        out: str,
        vcf_type: str = "auto",
        ntasks: int = 2,
        intermediate_prefix: str = "pmerge_intermediate",
):
    if mergestr_main is None:
        raise BCFExtrasDependencyError("Could not import trtools.mergeSTR.mergeSTR:main (missing TRTools dependency?)")

    ntasks = min(max(ntasks, 2), 512)  # Keep ntasks between 2 and 512 inclusive
    group_size = math.ceil(len(vcfs) / ntasks)
    initial_merges = _merge_small_last(
        [vcfs[i:i+group_size] for i in range(0, len(vcfs), group_size)], group_size)

    start_time = datetime.utcnow()

    print(f"Running parallel-mergeSTR with {ntasks} processes (group size: {group_size}, output: {out})")
    print(f"\tStarted at {start_time}Z")

    # TODO: This could be slightly more efficient if it allowed the second level to process at the same time... oh well

    with multiprocessing.Pool(ntasks) as p:
        init_merge_jobs = [
            p.apply_async(_merge, (intermediate_prefix, idx, vcfs, vcf_type, 0, False))
            for idx, vcfs in enumerate(initial_merges)
        ]
        init_outputs = [j.get() for j in init_merge_jobs]

        compress_jobs = [p.apply_async(_compress, (vcf,)) for vcf in init_outputs]
        compress_outputs = [j.get() for j in compress_jobs]

    if len(init_outputs) == 1:
        # Don't merge a single file, rename instead
        os.rename(init_outputs[0], f"{out}.vcf")
    else:
        # We've now merged every group_size VCFs into intermediate files - time to merge those!
        _merge(out, None, compress_outputs, vcf_type, None, True)

    end_time = datetime.utcnow()

    print(f"\tFinished at {end_time}Z (took {end_time - start_time})")
