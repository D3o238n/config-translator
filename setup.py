from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="config-translator",
    version="1.0.0",
    author="D_3on",
    description="Транслятор учебного конфигурационного языка в YAML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/D3o238n/config-translator",
    packages=find_packages(where="."),
    package_dir={"": "."},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Compilers",
        "Topic :: Text Processing :: Markup",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "config-translator=src.cli:main",
        ],
    },
    include_package_data=True,
)