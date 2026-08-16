from setuptools import find_packages, setup

setup(
    name="adversemed-gen",
    version="0.1.0",
    description="LLM-assisted generator for adversarial medical multiple-choice questions where the correct behavior is abstention.",
    author="Dyuthi Vallamsetty",
    url="https://github.com/calnugget/dyuthi-research",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": ["pytest>=7", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "adversemed-gen=adversemed_gen.cli:main",
        ],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
)
