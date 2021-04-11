import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="m00sic", # Replace with your own username
    version="0.0.1",
    author="Miria Feng and Christopher Wolff",
    author_email="cwolff98@gmail.com",
    description="Tools for algorithmic music generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cwolffff/m00sic",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)