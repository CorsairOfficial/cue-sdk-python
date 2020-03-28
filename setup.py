import os
import platform
import re
import sys
from setuptools import setup


def read_version(filename='cuesdk/version.py'):
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


def package_files(directory):
    return [
        os.path.join('..', path, filename)
        for (path, directories, filenames) in os.walk(directory)
        for filename in filenames
    ]


setup(
    name="cuesdk",
    version=read_version(),
    packages=['cuesdk'],
    package_data={
        'cuesdk': package_files('cuesdk/bin'),
    },
    zip_safe=False,
    author="Corsair Memory, Inc.",
    license='MIT',
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
