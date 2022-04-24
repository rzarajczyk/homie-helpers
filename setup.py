import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="homie-helpers",
    version="0.0.5",
    description="A set of helpers for implementing Homie IoT Convention",
    author="Rafał Zarajczyk",
    author_email="rzarajczyk@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rzarajczyk/homie-helpers",
    keywords=["HOMIE", "MQTT"],
    packages=['homie_helpers'],
    package_dir={'homie_helpers': './src/homie_helpers'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["paho-mqtt>=1.3.0", "Homie4>=0.3.8"],
)