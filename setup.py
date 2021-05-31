import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aptible-api",
    version="0.3.0",
    author="Zachary Elliott",
    author_email="zellio@trialspark.com",
    description="Object Oriented interface for Aptible API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TrialSpark/aptible-api",
    project_urls={
        "Bug Tracker": "https://github.com/TrialSpark/aptible-api",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'PyYAML>=5.4',
        'inflection>=0.5',
        'requests>=2.25',
    ]
)
