import os
import platform
import re
import sys
from setuptools import setup


def read_version(filename='src/version.py'):
    """Parse a __version__ number from a source file"""
    with open(filename) as source:
        text = source.read()
        match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", text)
        if not match:
            msg = "Unable to find version number in {}".format(filename)
            raise RuntimeError(msg)
        version = match.group(1)
        return version


arch, exetype = platform.architecture()
system = platform.system().lower()

if not system == 'windows':
    msg = "{} system is not supported".format(system)
    raise RuntimeError(msg)

data_files = []
lib_x86 = os.path.join('.', 'dll', 'CUESDK_2017.dll')
lib_x64 = os.path.join('.', 'dll', 'CUESDK.x64_2017.dll')
if os.path.exists(lib_x86) and os.path.exists(lib_x64):
    install_libdir = os.path.join(sys.prefix, 'DLLs')
    data_files.append((install_libdir, [lib_x86]))
    data_files.append((install_libdir, [lib_x64]))

setup(
    name="cuesdk",
    version=read_version(),
    packages=['cuesdk'],
    package_dir={'cuesdk': 'src'},
    data_files=data_files,
    zip_safe=False,
    author="Corsair Memory, Inc.",
    url="https://github.com/CorsairOfficial/cue-sdk-python",
    description="Ctypes-based CUE SDK binding for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[],
    platforms=['win'],
    python_requires='>=3.3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Games/Entertainment',
        'Topic :: System :: Hardware'
    ]
)

if not data_files:
    print("\nWARNING: Could not find %s" % lib_path)
