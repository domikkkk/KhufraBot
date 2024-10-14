from setuptools import setup, find_packages

setup(
    name="Ikariam",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'Ikariam': ['C/ika.so'],
        'Jap': ['*.json']
    },
    install_requires=[
        "requests>=2.32.3",
        "numpy>=1.26.4",
        "pandas>=2.2.2",
        "discord.py>=2.4.0"
    ],
    author="Dominik",
    author_email="domik141202@gmail.com",
    description="For Ikariam",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/domikkkk/KhufraBot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
