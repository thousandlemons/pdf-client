from distutils.core import setup

setup(
    name="pdf_client",

    version="1.3",

    author="SUN Ximeng (Nathaniel)",
    author_email="nathaniel@bretty.io",

    packages=["pdf_client", "pdf_client.api"],

    include_package_data=True,

    url="https://github.com/nathanielove/pdf-client",

    license="LICENSE.txt",

    description="A python client library for a more pleasant experience with pdf-server",
    long_description=open("README.txt").read(),

    install_requires=[
        "requests",
    ],
)
