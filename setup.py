#!/usr/bin/env python

# Automatically generated by nengo-bones, do not edit this file directly

import io
import os
import runpy

try:
    from setuptools import find_packages, setup
except ImportError:
    raise ImportError(
        "'setuptools' is required but not installed. To install it, "
        "follow the instructions at "
        "https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py"
    )


def read(*filenames, **kwargs):
    encoding = kwargs.get("encoding", "utf-8")
    sep = kwargs.get("sep", "\n")
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


root = os.path.dirname(os.path.realpath(__file__))
version = runpy.run_path(os.path.join(root, "nengo_dl", "version.py"))["version"]

import pkg_resources
import sys

# determine which tensorflow package to require
if "bdist_wheel" in sys.argv:
    # when building wheels we have to pick a requirement ahead of time (can't
    # check it at install time). so we'll go with tensorflow (non-gpu), since
    # that is the safest option
    tf_req = "tensorflow"
else:
    # check if one of the tensorflow packages is already installed (so that we
    # don't force tensorflow to be installed if e.g. tensorflow-gpu is already
    # there).
    # as of pep517 and pip>=10.0, pip will be running this file inside an isolated
    # environment, so we can't just look up the tensorflow version in the current
    # environment. but the pip package will be in the isolated sys.path, so we can use
    # that to look up the site-packages directory of the original environment.
    target_path = os.path.join("site-packages", "pip")
    for path in sys.path:
        if target_path in path:
            source_path = [path[: path.index("pip")]]
            break
    else:
        # fallback if we're not in an isolated environment (i.e. pip<10.0)
        source_path = sys.path
    installed_dists = [d.project_name for d in pkg_resources.WorkingSet(source_path)]
    for d in ["tf-nightly-gpu", "tf-nightly", "tensorflow-gpu"]:
        if d in installed_dists:
            tf_req = d
            break
    else:
        tf_req = "tensorflow"

install_req = [
    "nengo>=2.8.0",
    "numpy>=1.14.5",
    "%s>=2.0.0" % tf_req,
    "jinja2>=2.10.1",
    "progressbar2>=3.39.0",
]
docs_req = [
    "click>=6.7",
    "jupyter>=1.0.0",
    "matplotlib>=2.0.0",
    "nbsphinx>=0.3.5",
    "nengo-sphinx-theme>=0.7.0",
    "numpydoc>=0.6.0",
    "Pillow>=4.1.1",
    "sphinx>=1.8.0",
    "sphinx-click>=1.4.1",
]
optional_req = []
tests_req = [
    "attrs<19.2.0",
    "click>=6.7",
    "codespell>=1.12.0",
    "matplotlib>=2.0.0,<3.1.0",
    "nbval>=0.6.0",
    "pylint>=1.9.2",
    "pytest>=3.6.0,<4.1.0",
    "pytest-allclose>=1.0.0",
    "pytest-cov>=2.6.0",
    "pytest-rng>=1.0.0",
    "pytest-xdist>=1.16.0,<1.28.0",
    "six>=1.11.0",
]

setup(
    name="nengo-dl",
    version=version,
    author="Applied Brain Research",
    author_email="info@appliedbrainresearch.com",
    packages=find_packages(),
    url="https://www.nengo.ai/nengo-dl",
    include_package_data=True,
    license="Free for non-commercial use",
    description="Deep learning integration for Nengo",
    long_description=read("README.rst", "CHANGES.rst"),
    zip_safe=False,
    install_requires=install_req,
    extras_require={
        "all": docs_req + optional_req + tests_req,
        "docs": docs_req,
        "optional": optional_req,
        "tests": tests_req,
    },
    python_requires=">=3.5",
    entry_points={"nengo.backends": ["dl = nengo_dl:Simulator",],},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Nengo",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
