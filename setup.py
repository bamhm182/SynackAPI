import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name="SynackAPI",
    version="0.0.0",
    author="bamhm182",
    author_email="bamhm182@gmail.com",
    description="A package to interact with Synack's API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.github.com/bamhm182/synackAPI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    packages=['synack', 'synack.plugins'],
    package_dir={'':'src'},
    install_requires=[
        "netaddr==0.8.0",
        "pathlib2==2.3.5",
        "psycopg2-binary==2.9.1",
        "pyaml==21.8.3",
        "pyotp==2.6.0",
        "requests==2.25.1",
        "urllib3==1.26.3",
    ]
)
