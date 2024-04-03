import io
import os

from setuptools import find_packages, setup

# package meta-data
NAME = "trivela"
DESCRIPTION = "Trivela Python Web Framework build for learning purpose."
EMAIL = "rainamite@gmail.com"
AUTHOR = "Sanjaya Rai"
REQUIRES_PYTHON = ">=3.12.0"
VERSION = "0.0.4"

# which packages are required for this module to be executed?
REQUIRED = [
    "Jinja==3.1.2",
    "parse==1.20.0",
    "requests==2.31.0",
    "requests-wsgi-adapter==0.4.1",
    "WebOb==1.8.7",
    "whitenoise==4.1.4",
]

here = os.path.abspath(os.path.dirname(__file__))

# import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=["test_*"]),
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.12",
    ],
    setup_requires=["wheel"],
)
