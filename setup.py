"""
Setup configuration for PyAutoPytest Framework
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pyautopytest",
    version="0.1.0",
    author="Khalil Abu Assi",
    author_email="engkhalil.assi@gmail.com",
    description="A comprehensive test automation framework for web, API, and mobile testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Khalilassi/PyAutoPytest",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.4.0",
        "pytest-html>=3.2.0",
        "pytest-xdist>=3.3.0",
        "selenium>=4.15.0",
        "requests>=2.31.0",
        "Appium-Python-Client>=3.1.0",
        "PyYAML>=6.0.1",
        "colorlog>=6.7.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
)
