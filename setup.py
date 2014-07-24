from setuptools import setup, find_packages
setup(
    name = "python-feedly",
    version = "0.1",
    packages = find_packages(),
    install_required=["requests"]
)