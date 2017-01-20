
project = dict(
    # Changing these attributes is not supported (you'll have to manually move and edit files)
    name='soylent-recipes',  # PyPI (or other index) name.
    package_name='soylent_recipes',  # name of the root package of this project, e.g. 'myproject' or 'myproject.subproject' 
    human_friendly_name='Soylent Recipes',
    
    #
    description='Mine a food database for food combinations that match a nutrient profile',
    author='Tim Diels',  # will appear in copyright mentioned in documentation: 'year, your name'
    author_email='timdiels.m@gmail.com',
    python_version=(3,5),  # python (major, minor) version to use to create the venv and to test with. E.g. (3,5) for python 3.5.x. Only being able to pick a single version is a current shortcoming of Chicken Turtle Project.
    readme_file='README.md',
    url='https://github.com/timdiels/soylent-recipes', # project homepage
    download_url='https://github.com/timdiels/chicken_turtle_util/releases/v{version}.tar.gz', # Template for url to download source archive from. You can refer to the current version with {version}. You can get one from github or gitlab for example.
    license='GPL3',
 
    # What does your project relate to?
    keywords='soylent diet-problem',
    
    # Package indices to release to using `ct-release`
    # These names refer to those defined in ~/.pypirc.
    # For pypi, see http://peterdowns.com/posts/first-time-with-pypi.html
    # For devpi, see http://doc.devpi.net/latest/userman/devpi_misc.html#using-plain-setup-py-for-uploading
    index_test = 'pypitest',  # Index to use for testing a release, before releasing to `index_production`. `index_test` can be omitted if you have no test index
    index_production = 'pypi',
    
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    # Note: you must add ancestors of any applicable classifier too
    classifiers='''
        Development Status :: 2 - Pre-Alpha
        License :: OSI Approved
        Natural Language :: English
        Operating System :: POSIX
        Operating System :: POSIX :: AIX
        Operating System :: POSIX :: BSD
        Operating System :: POSIX :: BSD :: BSD/OS
        Operating System :: POSIX :: BSD :: FreeBSD
        Operating System :: POSIX :: BSD :: NetBSD
        Operating System :: POSIX :: BSD :: OpenBSD
        Operating System :: POSIX :: GNU Hurd
        Operating System :: POSIX :: HP-UX
        Operating System :: POSIX :: IRIX
        Operating System :: POSIX :: Linux
        Operating System :: POSIX :: Other
        Operating System :: POSIX :: SCO
        Operating System :: POSIX :: SunOS/Solaris
        Operating System :: Unix
        Programming Language :: Python
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3 :: Only
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: 3.4
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: Implementation
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: Stackless
    ''',
 
    # Auto generate entry points (optional)
    entry_points={
        'console_scripts': [
            'soylent = soylent_recipes.main:main', # just an example, any module will do, this template doesn't care where you put it
        ],
    },
    
    # pre_commit_no_ignore (optional):
    #
    # Files not to ignore in pre commit checks, despite them not being tracked by
    # git.
    #
    # Before a commit, project files are updated (ct-mkproject), the venv is
    # updated (ct-mkvenv), tests are run and documentation generation is checked
    # for errors. This process (intentionally) ignores any untracked files.
    # In order to include files needed by this process that you do not wish to
    # have tracked (e.g. files with passwords such as some test configurations),
    # you must add them to `pre_commit_no_ignore`.
    #
    # List of glob patterns relative to this file. You may not refer to files
    # outside the project directory (i.e. no higher than project.py).
    #
    # For supported glob syntax, see Python `glob.glob(recursive=False)`. Note
    # there is no need for ``**`` as no- ignores are recursive.
    pre_commit_no_ignore = [
        'data',
    ]
)
