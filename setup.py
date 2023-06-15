"""
    setup.py is responsible for:
    * Install dependencies
    * Define the package
"""

import re
from os import path
from setuptools import find_packages, setup
from typing import List

jobs_folder_name: str = "bounce_challenge"
current_path: str = path.abspath(path.dirname(__file__))
project_version: str = ""
readme_content: str = ""

# holds the setup install requirements
requires: List[str] = []

# holds the setup test requirements
test_requires: List[str] = []

# holds the setup requirements
setup_requires: List[str] = []

# get package version
with open(path.join(current_path, jobs_folder_name, "__init__.py"), encoding="utf-8") as f:
    result = re.search(r'__version__ = ["\']([^"\']+)', f.read())

    # if the contents of the __init__.py file are missing raise an error
    if not result:
        raise ValueError(f"Setuptools::open(): can't find package version in \
            {jobs_folder_name}/__init__.py")

    project_version = result.group(1)

# get the dependencies and installs
with open("requirements.txt", encoding="utf-8") as f:
    requires = [x.strip() for x in f if x.strip()]

# get test dependencies and installs
with open("requirements-test.txt", encoding="utf-8") as f:
    test_requires = [x.strip()
                     for x in f if x.strip() and not x.startswith("-r")]

# get setup dependencies and installs
with open("requirements-setup.txt", encoding="utf-8") as f:
    setup_requires = [x.strip()
                      for x in f if x.strip() and not x.startswith("-r")]

# get the long description from the README file
with open(path.join(current_path, "README.md"), encoding="utf-8") as f:
    readme_content = f.read()

extras = {
    'tests': test_requires,
}

setup(
    name="bounce_challenge",
    version=project_version,
    description="Challenge solutions for bounceapp",
    license="None",
    long_description=readme_content,
    long_description_content_type="text/markdown",
    url="https://github.com/guilherme-b/bounce_challenge",
    packages=find_packages(exclude=["tests.*"]),
    python_requires=">=3.9",
    include_package_data=False,
    install_requires=requires,
    setup_requires=setup_requires,
    extras_require={
        'tests': test_requires,
    },
    author="Guilherme Banhudo",
    entry_points={
        'jobs_runner': [
            'run_job=bounce_challenge.__main__:main'
        ]
    },
    zip_safe=False,
    keywords="bounce, scrapers, sql",
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Data Engineers"
    ]
)
