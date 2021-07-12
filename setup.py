import setuptools
__VERSION__ = "0.2.0"

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slsmanager",
    version=__VERSION__,
    author="Ainesh Sootha",
    author_email="aineshsootha@gmail.com",
    description="A basic tool that simplifies the deployment of AWS lambda functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AineshSootha/serverlessManager",
    project_urls={
        "Bug Tracker": "https://github.com/AineshSootha/serverlessManager/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires = [
        'click',
        'pathlib',
        'colorama',
        'boto3',
        'progress',
        'glob2',
        'pyyaml'
    ],
    entry_points = {
        'console_scripts': ['slsmanager = slsmanager.manager:main']
    }
)