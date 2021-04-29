# bcf_extras

![Test Status](https://github.com/davidlougheed/bcf_extras/workflows/Tests/badge.svg)

Extra variant file helper utilities built on top of `bcftools` and `htslib`.


## License

`bcf_extras` is licensed under GPLv3. See [the license](./LICENSE) for more 
information.


## Dependencies

The package requires that `bcftools` and `htslib` are installed on your 
operating system.


## What's Included

### `copy-compress-index`

Creates a `.vcf.gz` with a corresponding tabix index from a VCF, sorting the 
VCF if necessary.

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
following command on [`tests/vcfs/ahl.vcf`](tests/vcfs/ahl.vcf, replacing the 
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
