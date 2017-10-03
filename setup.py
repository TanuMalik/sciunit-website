import os
from setuptools import setup


def localopen(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


setup(name='sciunit_webpage_oauth',
      version='0.1',
      description='Sciunit-CLI website with Oauth callback route',
      long_description=localopen('README.md').read(),
      keywords=['sciunit', 'flask', 'geotrust'],
      url='https://bitbucket.org/geotrust/sciunit-website-2',
      author='John Gorman',
      author_email='jack.m.gman@gmail.com',
      license='MIT',
      packages=['sciunit_webpage_oauth'],
      install_requires=localopen('requirements.txt').readlines(),
      include_package_data=True,
      zip_safe=False)
