from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bao",
    version="0.1.1a0",
    author="Ong Yong Xin",
    author_email="ongyongxin.offical@gmail.com",
    description="Placeholder for the bao script manager (WIP)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/onyxware/bao",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.7",
    install_requires=["requests", "userdefaults3",],
)
