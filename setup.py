from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pymoleculer',
    version='0.1',
    description='Python implementation of Moleculer framework',
    author='Mirza',
    author_email='sayheymirza@gmail.com',
    packages=['pymoleculer', "pymoleculer/core", "pymoleculer/serializers", "pymoleculer/transporters"],
    install_requires=[
        'paho-mqtt',
        'psutil',
    ],
    license='MIT',
    url='https://heymirza.ir',
    # set readme file
    long_description=long_description,
    long_description_content_type="text/markdown", 
)
