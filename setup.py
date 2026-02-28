from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="asset_rounding",
    version="0.0.1",
    description="Rounds asset depreciation amounts per currency",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
