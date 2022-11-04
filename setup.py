from setuptools import setup, find_packages

setup(
    name="ARCoder",
    version="0.1.0",
    author="Seth Bromberger",
    author_email="github@bromberger.com",
    description="Implementation of the ARCoder Transliterated Arabic Name Matching Encoding Algorithm",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
    packages=find_packages(exclude=['tests.*', '*tests'])
)
