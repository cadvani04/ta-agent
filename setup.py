from setuptools import setup, find_packages

setup(
    name="agents_backend",
    version="0.1.0",
    packages=find_packages(where="backend", include=["discord_agent*", "canvas_agent*"]),
    package_dir={"": "backend"},
)