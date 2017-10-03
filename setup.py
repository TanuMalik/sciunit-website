from setuptools import setup

setup(name='sciunit_webpage_oauth',
      version='0.1',
      description='Sciunit-CLI website with Oauth callback route',
      keywords='sciunit flask geotrust',
      url='https://bitbucket.org/geotrust/sciunit-website-2',
      author='John Gorman',
      author_email='jack.m.gman@gmail.com',
      license='MIT',
      packages=['sciunit_webpage_oauth'],
      install_requires=[
          'Flask',
          'flask_mail',
          'gevent',
          'gunicorn'
      ],
      include_package_data=True,
      zip_safe=False)
