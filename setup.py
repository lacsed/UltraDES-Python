import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ultrades-python", # Replace with your own username
    version="0.0.1",
    author="LACSED Developers",
    author_email="lacsed.ufmg@gmail.com",
    description="A library for analysis ando control of Discrete Event Systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lacsed/ultrades",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[('lib\\site-packages\\', ['ultrades\\UltraDES.dll'])],
    python_requires='>=3.6',
)