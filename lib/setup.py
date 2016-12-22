from setuptools import setup

setup(name='orinoco',
      version='0.1',
      description='Sweet data integration',
      author='Quartic Technologies',
      author_email='alex@quartic.io',
      license='MIT',
      packages=['orinoco'],
      install_requires=[
          'aiohttp',
          'pyformance'
      ],
      zip_safe=False)
