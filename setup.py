import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bao",
    version="0.1.0-alpha",
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
    py_modules=["bao"],
    python_requires=">=3.7",
    install_requires=["requests", "userdefaults3",],
)
