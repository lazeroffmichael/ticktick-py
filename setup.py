import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ticktick-py", 
    version="1.0.0",
    author="Michael Lazeroff",
    author_email="lazeroffmichael@gmail.com",
    description="Unofficial API for TickTick.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lazeroffmichael/ticktick-py",
    packages=setuptools.find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
