from setuptools import setup, find_packages

setup(
    name="image-sorter-pro",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Pillow==9.5.0",
        "ttkbootstrap==1.10.1",
    ],
    entry_points={
        "console_scripts": [
            "image-sorter-pro=app:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful desktop application for organizing and sorting image files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/image-sorter-pro",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)