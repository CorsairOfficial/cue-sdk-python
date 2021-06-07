# cue-sdk-python

[![PyPI license](https://img.shields.io/pypi/l/cuesdk.svg?style=for-the-badge)](https://pypi.org/project/cuesdk)
[![PyPI version info](https://img.shields.io/pypi/v/cuesdk.svg?style=for-the-badge)](https://pypi.org/project/cuesdk)
[![PyPI supported Python versions](https://img.shields.io/pypi/pyversions/cuesdk.svg?style=for-the-badge)](https://pypi.org/project/cuesdk)

# Intro

This repository is dedicated for a `cuesdk` package on [PyPI](https://pypi.org/project/cuesdk)

`cuesdk` package is a `ctypes`-based CUE SDK binding for Python 3

# Requirements

`cuesdk` can be used on the following platforms:

- Windows 7 (32-bit and 64-bit);
- Windows 8, 8.1 (32-bit and 64-bit);
- Windows 10 (32-bit and 64-bit);
- macOS 10.13;
- macOS 10.14;
- macOS 10.15.

# Prerequisites

- Python 3.5 or higher. Support for earlier versions of Python is not provided. Python 2.7 or lower is not supported.

## Windows:

- iCUE for Windows https://www.corsair.com/icue
- Microsoft Visual C++ Redistributable for Visual Studio 2017.
  - x86 https://aka.ms/vs/15/release/VC_redist.x86.exe
  - x64 https://aka.ms/vs/15/release/VC_redist.x64.exe

## macOS:

- iCUE for macOS https://www.corsair.com/icue-mac

# Installing

You can install the package from [PyPI](https://pypi.org/project/cuesdk):

```sh
   # Windows
   $ py -3 -m pip install -U cuesdk
```

```sh
   # macOS
   $ python3 -m pip install -U cuesdk
```

# Usage

```python
from cuesdk import CueSdk

sdk = CueSdk()
sdk.connect()

print(sdk.protocol_details)

print(sdk.get_devices())

```

# Links

- API reference: https://github.com/corsairofficial/cue-sdk-python/blob/master/api_reference.md
- Code examples: https://github.com/corsairofficial/cue-sdk-python/tree/master/example
