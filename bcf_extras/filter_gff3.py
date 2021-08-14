import re
import sys
from typing import Optional

__all__ = [
    "filter_gff3",
]


def _compile_if_not_none(pattern: Optional[str]) -> Optional[re.Pattern]:
    # I wish for monads
    return re.compile(pattern) if pattern is not None else None


def filter_gff3(gff_file: str, seq_id: Optional[str], source: Optional[str], feature_type: Optional[str],
                strand: Optional[str], phase: Optional[str], no_body_comments: bool = False):
    # TODO: Add support for reading from bgzip file
    # TODO: Add support for querying scalar values
    # TODO: Add support for attribute querying

    seq_id = _compile_if_not_none(seq_id)
    source = _compile_if_not_none(source)
    feature_type = _compile_if_not_none(feature_type)
    strand = _compile_if_not_none(strand)
    phase = _compile_if_not_none(phase)

    done_header = False

    with open(gff_file, "r") as gf:
        for line in gf:
            if not line.strip() or line[0] == "#":
                if not (done_header and no_body_comments):
                    sys.stdout.write(line)
                continue

            done_header = True

            l_split = line.strip().split("\t")

            res = True

            if seq_id is not None:
                res = res and bool(seq_id.match(l_split[0]))
            if source is not None:
                res = res and bool(source.match(l_split[1]))
            if feature_type is not None:
                res = res and bool(feature_type.match(l_split[2]))
            if strand is not None:
                res = res and bool(strand.match(l_split[6]))
            if phase is not None:
                res = res and bool(phase.match(l_split[7]))

            if res:
                sys.stdout.write(line)
