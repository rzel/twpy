import setuptools

with open("README.md", "r", encoding="utf-8") as fhand:
    long_description = fhand.read()

setuptools.setup(
    name="tiddlywiki",
    version="0.0.5",
    #scripts=['twpym', 'twpye'],    
    author="Rob Zel",
    author_email="contact@robzel.com",
    description=("A full featured desktop client "
                "for editing and managing TiddlyWiki html files - simple, powerful, elegant and efficient."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://twpy.org",
    project_urls={
        "Bug Tracker": "https://twpy.org/bugs",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pywebview"],
    #packages=setuptools.find_packages(),
    packages=['tiddlywiki'], # setuptools.find_packages(),
    package_dir={"tiddlywiki":""},
    package_data={
    'tiddlywiki': ['defaultworkspacelist.html'], # ['../*.html']
    },
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "twpym = tiddlywiki.twpym:start_twpy_manager",
            "twpye = tiddlywiki.twpye:start_twpy_editor",
        ]
    }
)
