from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcnp6-ai-assistant",
    version="1.0.0",
    author="核工程与核技术专业",
    author_email="",
    description="一个整合AI和MCNP6的Windows桌面应用程序",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcnp6-ai-assistant",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "psutil>=5.9.0",
        "pygments>=2.17.0",
        "qdarkstyle>=3.2.0",
    ],
    entry_points={
        "console_scripts": [
            "mcnp6-ai=main:main",
        ],
    },
)
