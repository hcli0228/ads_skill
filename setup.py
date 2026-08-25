from setuptools import setup, find_packages

setup(
    name="ads-skill",
    version="0.1.0",
    packages=find_packages(include=["ads_api*", "scripts*"]),
)
