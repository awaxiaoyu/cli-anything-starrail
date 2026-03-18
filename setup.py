"""Setup script for StarRailCopilotPro."""

from setuptools import setup, find_namespace_packages

setup(
    name="starrailcopilotpro",
    version="1.0.0",
    description="StarRailCopilotPro - Professional CLI interface for StarRailCopilot automation",
    author="StarRailCopilot Team",
    author_email="",
    url="https://github.com/awaxiaoyu/cli-anything-starrail",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "starrail-pro=cli_anything.starrail.starrail_cli:main",
            "starrailcopilotpro=cli_anything.starrail.starrail_cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Automation",
    ],
    keywords="starrail honkai automation cli agent ai starrailcopilot",
)
