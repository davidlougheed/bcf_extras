# bcf_extras

![Test Status](https://github.com/davidlougheed/bcf_extras/workflows/Tests/badge.svg)

Extra variant file helper utilities built on top of `bcftools` and `htslib`.


## License

`bcf_extras` is licensed under GPLv3. See [the license](./LICENSE) for more 
information.


## Dependencies

The package requires that `bcftools` and `htslib` are installed on your 
operating system.

For the `str` extra, `TRtools` is required as a pip dependency. This should be
handled automatically upon installation, but I have encountered installation 
issues before (especially when copies of `htslib` interfere with one another.)
Feel free to file an issue to ask about this.


## Installation

One can use pip to install either the base `bcf-extras` or `bcf-extras[str]`,
which has additional dependencies and adds some more utilities related to STR
calling.

```bash
pip install bcf-extras
# or
pip install bcf-extras[str]
```


## What's Included (Base)

### `copy-compress-index`

Creates `.vcf.gz` files with a corresponding tabix indices from one or more 
VCFs, sorting the VCFs if necessary.

For example, the following would generate `sample-1.vcf.gz` and `sample-1.vcf.gz.tbi`:

```bash
bcf-extras copy-compress-index sample-1.vcf
```

### `add-header-lines`

Adds header lines from a text file to a particular position in the VCF header.
Useful for e.g. inserting missing `##contig` lines to a bunch of VCFs at once
(taking advantage of this + something like GNU parallel.)

For the `##contig` lines example, inserting the contents of 
[`tests/vcfs/new_lines.txt`](tests/vcfs/new_lines.txt), we could run the 
following command on [`tests/vcfs/ahl.vcf`](tests/vcfs/ahl.vcf), replacing the 
file with a new copy:

```bash
bcf-extras add-header-lines tests/vcfs/ahl.vcf tests/vcfs/new_lines.txt
```

There is also a flag, `--tmp-dir`, for specifying a temporary folder location
into which header artifacts will be placed. This is especially useful when 
running jobs on clusters, which may have specific locations for temporary I/O.

Using GNU parallel, we can do multiple VCFs at once, e.g.:

```bash
parallel 'bcf-extras add-header-lines {} tests/vcfs/new_lines.txt --keep-old' ::: /path/to/my/vcfs/*.vcf
```

The `--keep-old` flag keeps the original VCFs as a copy.

### `arg-join`

Some bioinformatics utilities take in comma-separated file lists rather than 
the more standard whitespace-separated lists that something like a glob 
(`*.vcf.gz`) generates.

This command can be run by itself, e.g.:

```bash
bcf-extras arg-join --sep ";" *.vcf
# Outputs e.g. sample1.vcf;sample2.vcf
```

It can be used embedded in another command, e.g. with `mergeSTR`,
[a tool for merging STR caller VCFs](https://github.com/gymreklab/TRTools)
which takes as input a *comma-separated* list of files:

```bash
mergeSTR --vcfs $(bcf-extras arg-join *.vcf) --out my_merge
```

The default separator (specified via `--sep`) is `,`.

### `filter-gff3`

This command can filter a GFF3 (or similarly formatted) file and filter it
by various columns using regular expressions.

It prints the filtered lines to `stdout`, which can then be redirected to a 
file or piped to another process.

Currently, you can filter by the `seqid`, `source`, `type`, `strand`, and 
`phrase` columns using Python-formatted regular expressions, e.g. the 
following, which filters `type` to be either `gene` or `exon` and stores that
in a new file:

```bash
bcf-extras filter-gff3 --type '^(gene|exon)$' example.gff3 > example-genes-exons.gff3
```

To create a TABIX-indexable, compressible GFF3 file, you can use the 
`--no-body-comments` flag to remove in-file comments that could interfere.

For help, run the sub-command with no arguments:

```bash
bcf-extras filter-gff3
```


## What's Included (STR)

### `parallel-mergeSTR`

[mergeSTR](https://github.com/gymreklab/TRTools) is a tool by the Gymrek lab
used to merge STR call VCFs. It proceeds linearly over a list of files, which
cannot easily take advantage of multiple cores. This utility merges VCFs in a 
tree fashion to produce a final merged result, and is handy when merging 100s
of STR call VCFs at once.

```bash
bcf-extras parallel-mergeSTR *.vcf.gz --out my_merge --ntasks 10
```

In a dataset of 148 single-sample gangSTR call VCFs, merging with 
`parallel-mergeSTR` on 10 cores resulted in an 60% speedup versus
running on a single core (~2 hours versus ~5 hours.)

Speedup is not linear with number of cores used, so it only makes sense to use
this if turnaround time is important and resources are available.

To not over-allocate resources on a cluster, the process can be split further
into first a parallelized task, and then a task which only uses one core:

```bash
# Runs on multiple cores
bcf-extras parallel-mergeSTR *.vcf.gz --ntasks 10 --out my_merge --step1-only

# Intermediate files generated by the first step will feed into the second step.

# Bottlenecked single process step; the ntasks argument is still needed to 
# calculate the names of the intermediate output files (but sub-processes are 
# not spawned) - thus, the provided value must match the value above.
bcf-extras parallel-mergeSTR --ntasks 10 --out my_merge --step2-only
```
