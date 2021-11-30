import math
import multiprocessing
import os
import subprocess

from argparse import Namespace
from datetime import datetime
from typing import List, Optional

from .exceptions import BCFExtrasDependencyError, BCFExtrasInputError

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


def _intermediate_file_name(prefix: str, idx: Optional[int]):
    return f"{prefix}_{idx}" if idx is not None else prefix


def _merge(
        out_file_prefix: str,
        vcfs: List[str],
        vcf_type: str,
        remove_previous: bool
):
    print(f"\tMerging [{', '.join(vcfs)}] to {out_file_prefix}.vcf", flush=True)

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
            try:
                os.remove(f"{vcf}.tbi")
            except FileNotFoundError:
                pass

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
        step_1_only: bool = False,
        step_2_only: bool = False,
        intermediate_prefix: Optional[str] = None,
):
    if mergestr_main is None:
        raise BCFExtrasDependencyError("Could not import trtools.mergeSTR.mergeSTR:main (missing TRTools dependency?)")

    if step_1_only and step_2_only:
        raise BCFExtrasInputError("Cannot specify both --step1-only and --step2-only")

    run_step_1 = step_1_only or not (step_1_only or step_2_only)
    run_step_2 = step_2_only or not (step_1_only or step_2_only)

    if intermediate_prefix is None:
        intermediate_prefix = f"pmerge_intermediate_{out}"

    ntasks = min(max(ntasks, 2), 512)  # Keep ntasks between 2 and 512 inclusive
    group_size = math.floor(len(vcfs) / ntasks)
    initial_merges = _merge_small_last(
        [vcfs[i:i+group_size] for i in range(0, len(vcfs), group_size)], group_size)

    start_time = datetime.utcnow()

    print(f"Running parallel-mergeSTR with {ntasks} processes (group size: {group_size}, output: {out})")
    print(f"\tStarted at {start_time}Z")

    if step_1_only:
        print(f"\tRunning step 1 only (parallel, ntasks={ntasks})")
    elif step_2_only:
        print("\tRunning step 2 only (bottlenecked final merge step; single-core only)")

    # TODO: This could be slightly more efficient if it allowed the second level to process at the same time... oh well

    intermediate_vcf_names = [_intermediate_file_name(intermediate_prefix, idx) for idx in range(len(initial_merges))]

    if run_step_1:
        with multiprocessing.Pool(ntasks) as p:
            init_merge_jobs = [
                p.apply_async(_merge, (out_name, vcfs, vcf_type, False))
                for vcfs, out_name in zip(initial_merges, intermediate_vcf_names)
            ]
            init_outputs = [j.get() for j in init_merge_jobs]

            if len(init_outputs) > 1:
                compress_jobs = [p.apply_async(_compress, (vcf,)) for vcf in init_outputs]
                for j in compress_jobs:
                    j.get()

        if len(initial_merges) == 1:
            # Don't merge a single file, rename instead
            os.rename(f"{intermediate_vcf_names[0]}.vcf", f"{out}.vcf")
            print("\tStep 1 finished with only 1 output; step 2 is not needed")

    if run_step_2 and len(initial_merges) > 1:
        # We've now merged every group_size VCFs into intermediate files - time to merge those!
        _merge(out, [f"{ivn}.vcf.gz" for ivn in intermediate_vcf_names], vcf_type, True)

    end_time = datetime.utcnow()

    print(f"\tFinished at {end_time}Z (took {end_time - start_time})")
