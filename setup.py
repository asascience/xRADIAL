from setuptools import setup, find_packages

setup(
    name='xradial',
    version='0.0.1',
    author=['Dalton R. Kell', 'Brian McKenna', 'Michael Christensen'],
    packages=find_packages(),
    description='Library for converting HF-Radar Radial ASCII data to NetCDF format',
    long_description=open('README.md').read(),
)
