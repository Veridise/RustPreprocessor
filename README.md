# RustPreprocessor

The RustPreprocessor generates a `JSON` summary of a Rust contract that is used by [Vanguard](https://github.com/Veridise/Vanguard). 

- [Requirements](#requirements)
- [Build](#build)
- [Usage](#usage)

## Requirements

The RustPreprocessor has the following requirements:
 * Python3 (Version 3.8.9)

## Build

No build is necessary. Simply run the `summarizer.py` script to generate summaries.

## Usage

To generate a summary, run the following command:

```
python3 summarizer.py <PATH_TO_METADATA_JSON>
```

where `<PATH_TO_METADATA_JSON>` is the path to the `metadata.json` file created when using `cargo` to build a contract via the following command: `cargo +nightly contract build`. 

NOTE: This means the preprocessor indirectly requires `cargo` as well as [ink](https://github.com/paritytech/cargo-contract) and the `cargo nightly` build.
