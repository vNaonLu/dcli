from setuptools import setup, find_packages
from src.dcli import __version__
from pathlib import Path

PACKAGES = find_packages('src')

readme = ""
with Path("README.md").open("r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="decorator-cli",
    version=__version__,
    license="MIT",
    author="Naon Lu",
    author_email="vnaonlu0101453@gmail.com",
    packages=PACKAGES,
    package_dir={'': 'src'},
    url="https://github.com/vNaonLu/dcli",
    keywords="decorator cli",
    description="functional-oriented cli decorator.",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
