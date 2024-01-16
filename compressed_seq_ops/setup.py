from setuptools import setup, Extension

setup(
    name="crosswordist_native_index",
    version="0.0.1",
    author="karno-bh",
    author_email="karno.bh@gmail.com",
    description="Bitmap Operations for Crosswordist",
    license="MIT",
    keywords="bimap index",
    ext_modules=[
        Extension(
            name="crosswordist_native_index.compressed_seq",
            sources=["compressed_seq.c"]
        ),
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)