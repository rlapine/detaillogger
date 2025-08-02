from setuptools import setup, find_packages

setup(
    name="detaillogger",
    version="0.1.6",
    packages=find_packages(),  # This auto-discovers the 'detaillogger' folder
    include_package_data=True,
)