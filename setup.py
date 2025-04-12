"""
Setup script for the linkis-python-sdk package.
"""
import re

from setuptools import setup, find_packages

# Read version from __init__.py
with open('linkis_python_sdk/__init__.py', 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Failed to find version string.")

# Read long description from README_CN.md
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='linkis-python-sdk',
    version=version,
    description='Python SDK for Apache Linkis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='rogerhuang',
    author_email='haungli1279@163.com',
    url='https://github.com/huangli1279/linkis-python-sdk',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.24.0',
        'pandas>=1.0.0',
    ],
    keywords='linkis,apache,bigdata,sdk',
)
