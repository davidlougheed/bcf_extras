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
bcf-extras add-header-lines tests/vcfs/ahl.vcf tests/vcfs/new_lines.txt --delete-existing
```

There is also a flag, `--tmp-dir`, for specifying a temporary folder location
into which header artifacts will be placed. This is especially useful when 
running jobs on clusters, which may have specific locations for temporary I/O.

Using GNU parallel, we can do multiple VCFs at once, e.g.:

```bash
parallel 'bcf-extras add-header-lines {} tests/vcfs/new_lines.txt --delete-existing' ::: /path/to/my/vcfs/*.vcf
```

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


## What's Included (STR)

### `parallel-mergeSTR`

[mergeSTR](https://github.com/gymreklab/TRTools) is a tool by the Gymrek lab
used to merge STR call VCFs. It proceeds linearly over a list of files, which
cannot easily take advantage of multiple cores. This utility merges VCFs in a 
tree fashion to produce a final merged result, and is handy when merging 100s
of STR call VCFs at once.

```bash
bcf-extras parallel-mergeSTR *.vcf --out my_merge --ntasks 40
```
