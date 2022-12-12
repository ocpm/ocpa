# from setuptools import setup
import setuptools

from ocpa import __name__ as ocpa_name
from ocpa import __version__ as ocpa_version
from ocpa import __doc__ as ocpa_doc
from ocpa import __author__ as ocpa_author
from ocpa import __author_email__ as ocpa_authormail
setuptools.setup(
    name=ocpa_name,
    packages=setuptools.find_packages(),
    py_modules=[ocpa_name],
    include_package_data=True,
    version=ocpa_version,
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    description=ocpa_doc.strip(),
    author=ocpa_author,
    author_email=ocpa_authormail,
    # Provide either the link to your github or to your website
    url='https://github.com/ocpm/ocpa',
    install_requires=[            # I get to this in a second
            "pm4py<2.3.0",
            "scikit-learn<=0.24.2",
            "setuptools",
            "jsonschema",
    ],
    # classifiers=[
    # 'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    # 'Intended Audience :: Developers',      # Define that your audience are developers
    # 'Topic :: Software Development :: Build Tools',
    # 'License :: OSI Approved :: MIT License',   # Again, pick a license
    # 'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    # 'Programming Language :: Python :: 3.4',
    # 'Programming Language :: Python :: 3.5',
    # 'Programming Language :: Python :: 3.6',
    # ],
)
