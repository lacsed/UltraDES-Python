import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

print((os.path.join("lib", "site-packages", ""), os.path.join("ultrades", "UltraDES.dll")))

setuptools.setup(
    name="ultrades-python",
    version="0.0.3",
    author="LACSED Developers",
    author_email="lacsed.ufmg@gmail.com",
    description="A library for analysis and control of Discrete Event Systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lacsed/ultrades",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pycparser',
        'pythonnet>=2.5.0',
        'ipython'
    ],
    data_files=[(os.path.join("lib", "site-packages"), [os.path.join("ultrades", "UltraDES.dll")])],
    python_requires='>=3.6',
)