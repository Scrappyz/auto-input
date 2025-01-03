from setuptools import setup, find_packages

setup(
    name="auto-input",  # Replace with your package's name
    version="0.2.0-alpha",  # Replace with your version
    description="A tool for automating input using Python.",
    author="Your Name",  # Replace with your name
    author_email="your.email@example.com",  # Replace with your email
    url="https://github.com/yourusername/auto-input",  # Replace with your project's URL
    packages=find_packages(),  # Automatically find packages in your project
    install_requires=[
        "pynput",
        "bidict",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "auto-input=project.autoinput:main",
        ],
    },
    include_package_data=True,  # Includes non-Python files like `config.json`
)
