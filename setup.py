"""Packaging configuration for UltraDES-Python."""
from __future__ import annotations

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ultrades-python",
    version="0.0.7",
    author="LACSED Developers",
    author_email="lacsed.ufmg@gmail.com",
    description="A library for analysis and control of Discrete Event Systems",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lacsed/ultrades",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pycparser",
        "pythonnet>=3.0.0",
        "ipython",
    ],
    # The managed assembly is fetched on first use, not bundled into the wheel.
    package_data={},
    include_package_data=True,
    python_requires=">=3.8",
)
