# specification_extraction

[![CI](https://github.com/MattHag/specification-extraction/actions/workflows/build.yml/badge.svg)](https://github.com/MattHag/specification-extraction/actions/workflows/main.yml)

Awesome specification_extraction created by MattHag

## Install it from PyPI

```bash
pip install specification_extraction
```

## Usage

```py
from specification_extraction import BaseClass
from specification_extraction import base_function

BaseClass().base_method()
base_function()
```

```bash
$ python -m specification_extraction
#or
$ specification_extraction
```

## Development

Create and enable a virtual environment (e.g. `make virtualenv`), then run the following command to installs the
development dependencies and pre-commit hooks.

```bash
$ make install
```
