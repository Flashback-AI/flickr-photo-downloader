"""Module Setup."""

import runpy
from setuptools import setup, find_packages

# from distutils.core import setup

PACKAGE_NAME = "flickr-photo-downloader"
version_meta = runpy.run_path("./version.py")
VERSION = version_meta["__version__"]

with open("README.md", "r") as fh:
    long_description = fh.read()


def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    line_iter = (line.strip() for line in open(filename))
    return [line for line in line_iter if line and not line.startswith("#")]


if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        packages=find_packages(),
        scripts=["scripts/flickr-photo-downloader-cli"],
        license='MIT',
        description='Small utility to helps download Flickr Photo Sets / Albums & Photos in Bulk',
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Justin Kruger',
        author_email='jdavid.net@gmail.com',
        url='https://github.com/Flashback-AI/flickr-photo-downloader',
        download_url='https://github.com/Flashback-AI/flickr-photo-downloader/archive/main.zip',
        keywords=['python', 'photos', 'flickr'],
        install_requires=parse_requirements("requirements.txt"),
        python_requires=">=3.7.0",
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
    )
