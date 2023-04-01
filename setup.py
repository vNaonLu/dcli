from setuptools import setup, find_packages
from src.dcli.version import VERSION

PACKAGES = find_packages('src')

setup(
    name="dcli",
    version=VERSION,
    license="MIT",
    author="Naon Lu",
    author_email="vnaonlu0101453@gmail.com",
    packages=PACKAGES,
    package_dir={'': 'src'},
    url="https://github.com/vNaonLu/dcli",
    keywords="decorator cli",
    description="functional-oriented cli decorator.",
    long_description="functional-oriented command line interface decorator module.",
    python_requires=">=3.9"
)
