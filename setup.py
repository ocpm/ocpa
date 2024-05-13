# from setuptools import setup
import setuptools

from ocpa import __author__ as ocpa_author
from ocpa import __author_email__ as ocpa_authormail
from ocpa import __doc__ as ocpa_doc
from ocpa import __name__ as ocpa_name
from ocpa import __version__ as ocpa_version

setuptools.setup(
    name=ocpa_name,
    install_requires=[  # I get to this in a second
        "pm4py==2.2.32",
        "setuptools",
        "jsonschema",
    ],
    packages=setuptools.find_packages(),
    py_modules=[ocpa_name],
    include_package_data=True,
    version=ocpa_version,
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license="MIT",
    description=ocpa_doc.strip(),
    author=ocpa_author,
    author_email=ocpa_authormail,
    # Provide either the link to your github or to your website
    url="https://github.com/ocpm/ocpa",
)
