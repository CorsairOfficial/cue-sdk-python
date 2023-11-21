# cue-sdk-python

[![PyPI license](https://img.shields.io/pypi/l/cuesdk.svg?style=for-the-badge)](https://pypi.org/project/cuesdk)
[![PyPI version info](https://img.shields.io/pypi/v/cuesdk.svg?style=for-the-badge)](https://pypi.org/project/cuesdk)
[![PyPI supported Python versions](https://img.shields.io/pypi/pyversions/cuesdk.svg?style=for-the-badge)](https://pypi.org/project/cuesdk)

## Intro

This repository is dedicated for a `cuesdk` package on [PyPI](https://pypi.org/project/cuesdk)

`cuesdk` package is a `ctypes`-based CUE SDK binding for Python 3

## Requirements

`cuesdk` can be used on the following platforms:

- Windows 7 (x64);
- Windows 8, 8.1 (x64);
- Windows 10 (x64);
- Windows 11 (x64);
- macOS 10.13;
- macOS 10.14;
- macOS 10.15;
- macOS 11;

## Prerequisites

- Python 3.9 or higher. Support for earlier versions of Python is not provided. Python 2.7 or lower is not supported.

### Windows

- [iCUE for Windows](https://www.corsair.com/icue)
- Microsoft Visual C++ Redistributable for Visual Studio 2019.
  - x64 <https://aka.ms/vs/17/release/vc_redist.x64.exe>

### macOS

- [iCUE for macOS](https://www.corsair.com/icue-mac)

## Installing

You can install the package from [PyPI](https://pypi.org/project/cuesdk):

```sh
   # Windows
   $ py -3 -m pip install -U cuesdk
```

```sh
   # macOS
   $ python3 -m pip install -U cuesdk
```

## Usage

```python
from cuesdk import (CueSdk, CorsairDeviceFilter, CorsairDeviceType, CorsairError)

sdk = CueSdk()

def on_state_changed(evt):
   print(evt.state)

err = sdk.connect(on_state_changed)

details, err = sdk.get_session_details()
print(details)

devices, err = sdk.get_devices(
        CorsairDeviceFilter(device_type_mask=CorsairDeviceType.CDT_Keyboard))
if err == CorsairError.CE_Success:
   for d in devices:
      print(sdk.get_device_info(d.device_id))

```
