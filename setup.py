# setup.py

from setuptools import setup, find_packages

setup(
    name="customer_experience_analytics_for_fintech_apps",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
