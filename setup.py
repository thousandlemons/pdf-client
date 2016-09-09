from distutils.core import setup

setup(
    name="pdf-client",

    version="1.2",

    author="SUN Ximeng (Nathaniel)",
    author_email="nathaniel@bretty.io",

    packages=["pdf_client", "pdf_client.api", "pdf_client.multithread"],

    include_package_data=True,

    url="https://github.com/nathanielove/pdf-client",

    license="LICENSE.txt",

    description="A python client library to give you a more pleasant experience with pdf-server (https://github.com/nathanielove/pdf-server)",
    # long_description=open("README.txt").read(),

    install_requires=[
        "requests",
    ],
)
