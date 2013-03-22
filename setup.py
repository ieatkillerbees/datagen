import sys
import os
from setuptools import setup
import distribute_setup
distribute_setup.use_setuptools()

setup(name = "datagen",
      version = "0.9",
      description = "Random Data Generator",
      author = "Samantha Quinones",
      author_email = "squinones@politico.com",
      url = "http://www.politco.com/staffmembers/SamanthaQuinones.html",
      packages = ["datagen"],
      
      include_package_data = True,
      package_data = {'': ['distribute_setup.py', 'templates/*'], 'datagen': ['data/*']},
      install_requires = ["progressbar>=2.3", "pymongo>=2.4.2"],
      zip_safe = False,
      entry_points = {
            'console_scripts': ['datagen = datagen.script:start']
      }
)
