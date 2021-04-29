# bcf_extras

![Test Status](https://github.com/davidlougheed/bcf_extras/workflows/Test/badge.svg)

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

TODO: Usage

### `add-header-lines`

Adds header lines from a text file to a particular position in the VCF header.
Useful for e.g. inserting missing `##contig` lines to a bunch of VCFs at once
(taking advantage of this + something like GNU parallel.)

TODO: Usage
