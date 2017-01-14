# Auto generated by ct-mksetup
# Do not edit this file, edit ./project.py instead

from setuptools import setup
setup(
    **{   'author': 'Tim Diels',
    'author_email': 'timdiels.m@gmail.com',
    'classifiers': [   'Development Status :: 2 - Pre-Alpha',
                       'License :: OSI Approved',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Operating System :: POSIX :: AIX',
                       'Operating System :: POSIX :: BSD',
                       'Operating System :: POSIX :: BSD :: BSD/OS',
                       'Operating System :: POSIX :: BSD :: FreeBSD',
                       'Operating System :: POSIX :: BSD :: NetBSD',
                       'Operating System :: POSIX :: BSD :: OpenBSD',
                       'Operating System :: POSIX :: GNU Hurd',
                       'Operating System :: POSIX :: HP-UX',
                       'Operating System :: POSIX :: IRIX',
                       'Operating System :: POSIX :: Linux',
                       'Operating System :: POSIX :: Other',
                       'Operating System :: POSIX :: SCO',
                       'Operating System :: POSIX :: SunOS/Solaris',
                       'Operating System :: Unix',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 3',
                       'Programming Language :: Python :: 3 :: Only',
                       'Programming Language :: Python :: 3.2',
                       'Programming Language :: Python :: 3.3',
                       'Programming Language :: Python :: 3.4',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: Implementation',
                       'Programming Language :: Python :: Implementation :: CPython',
                       'Programming Language :: Python :: Implementation :: Stackless'],
    'description': 'Mine a food database for food combinations that match a nutrient profile',
    'entry_points': {'console_scripts': ['soylent = soylent_recipes.main:main']},
    'extras_require': {   'dev': ['numpydoc', 'sphinx', 'sphinx-rtd-theme'],
                          'test': ['pytest', 'pytest-env']},
    'install_requires': [   'attrs',
                            'chicken-turtle-util[click,test,data_frame,path,logging]==4.*',
                            'numpy',
                            'pandas',
                            'tabulate',
                            'pyprof2calltree',
                            'colored-traceback'],
    'keywords': 'soylent diet-problem',
    'license': 'GPL3',
    'long_description': 'soylent-recipes\n'
                        '===============\n'
                        '\n'
                        'Mines a food database for food combinations that match the nutrient\n'
                        'profile in the database. Current implementation leads to results that\n'
                        'match the target profile by 75%.\n'
                        '\n'
                        'Currently it uses the USDA database, but you could fill it up with other\n'
                        'food data as well.\n'
                        '\n'
                        'If you already know which foods you want to use for your soylent recipe\n'
                        'but simply want to know the amounts to take of each, use this [diet\n'
                        'problem applet] [http://www.neos-guide.org/content/dietproblem-demo].\n'
                        '\n'
                        'Usage\n'
                        '-----\n'
                        '\n'
                        '-  git clone https://github.com/timdiels/soylent-recipes.git\n'
                        '-  pip install .\n'
                        '-  Download food data from\n'
                        '   '
                        'https://www.ars.usda.gov/northeast-area/beltsville-md/beltsville-human-nutrition-research-center/nutrient-data-laboratory/docs/usda-national-nutrient-database-for-standard-reference/\n'
                        '-  Put it in data/usda\\_nutrient\\_db\\_sr28 (i.e. that directory contains\n'
                        '   files like NUTR\\_DEF.txt)\n'
                        '-  Run ``soylent``\n'
                        '\n'
                        'Status\n'
                        '------\n'
                        '\n'
                        'Having another go, this time using Python for faster development. The\n'
                        'C++ implementation contained a bug in its recipe scoring function (due\n'
                        'to lack of testing), as such previous results should be ignored (e.g. it\n'
                        'considered a diet of pure water to match the nutritional profile quite\n'
                        'well).\n'
                        '\n'
                        'Old\n'
                        '===\n'
                        '\n'
                        'Table of Contents\n'
                        '-----------------\n'
                        '\n'
                        '-  `Approach to solving the\n'
                        '   problem <#approach-to-solving-the-problem>`__\n'
                        '-  `Results <#results>`__\n'
                        '-  `System requirements <#system-requirements>`__\n'
                        '-  `Compilation <#compilation>`__\n'
                        '-  `Project history <#project-history>`__\n'
                        '\n'
                        'Approach to solving the problem\n'
                        '-------------------------------\n'
                        '\n'
                        'The problem is: finding combos of foods that make for good (soylent)\n'
                        'recipes, regardless of taste.\n'
                        '\n'
                        'Solving a single combo of foods is simple enough as explained in\n'
                        '`Recipe/Diet Problem <#recipe-diet-problem>`__.\n'
                        '\n'
                        'The mining phase entails choosing combinations of foods. Simply\n'
                        'enumerating all possible combinations would take years. After other\n'
                        "attempts we've settled with a genetic algorithm.\n"
                        '\n'
                        'Note: we could use subspace clustering, after which we may be able to\n'
                        'use this clustering to aid in making good food combinations.\n'
                        '\n'
                        'Recipe/Diet Problem\n'
                        '~~~~~~~~~~~~~~~~~~~\n'
                        '\n'
                        'First some more detailed definitions of this subproblem.\n'
                        '\n'
                        'Let a recipe problem be: given a set of foods, and a nutrition profile,\n'
                        'find the amounts to optimally satisfy the nutrition profile. (This is\n'
                        'more commonly known as a `Diet\n'
                        'Problem <http://www.neos-guide.org/content/diet-problem>`__)\n'
                        '\n'
                        'Each food has m properties/nutrients of an ingredient (the contained\n'
                        'amount of magnesium, carbs, ...).\n'
                        '\n'
                        'Construct a matrix A with: A\\_{i,j} = the amount of the i-th property of\n'
                        'the j-th food.\n'
                        '\n'
                        'With n foods, there are amounts X\\_1, ..., X\\_n to find.\n'
                        '\n'
                        'The nutrient profile provides us with Y\\_i and M\\_i for each nutrient.\n'
                        'Y\\_i is the desired amount of nutrient i, M\\_i is the max allowed amount\n'
                        'of nutrient i.\n'
                        '\n'
                        'This leads to - m equations, j=1,2,...m: X\\_1 A\\_{1,j} + ... + X\\_n\n'
                        'A\\_{n,j} = Y\\_i. - m inequalities, j=1,2,...m: X\\_1 A\\_{1,j} + ... +\n'
                        'X\\_n A\\_{n,j} <= M\\_i.\n'
                        '\n'
                        'Which is a constrained least squares problem.\n'
                        '\n'
                        'The algorithm used to solve this is an `active-set\n'
                        'algorithm <http://www.alglib.net/optimization/boundandlinearlyconstrained.php#header1>`__.\n'
                        '\n'
                        'The function f to mimimize is: :raw-latex:`\\lnorm `A\\*x - y\n'
                        ':raw-latex:`\\rnorm`\\_2\n'
                        '\n'
                        'The gradient of f(x) is: the vector D, j=1,2,...,n, D[j] = 2\n'
                        ':raw-latex:`\\sum`\\_{i=1}^m ((A\\*x-y)*i a*\\ {i,j})\n'
                        '\n'
                        'Last noted performance of solving a recipe in this project of on average\n'
                        '8.5 foods was 9834889 instructions (= callgrind instruction fetch cost)\n'
                        '\n'
                        'Results\n'
                        '-------\n'
                        '\n'
                        'Current results are mostly hilarious due to its total disregard for\n'
                        'taste.\n'
                        '\n'
                        "Obtaining the results isn't a very user friendly experience, but if\n"
                        "you're up to it:\n"
                        '\n'
                        '1. Run the miner with ./run.sh. It may take 45 minutes to compute.\n'
                        '2. The results are written to population.obm. Search that file for\n'
                        '   HallOfFame entries, as those are the best combinations the algorithm\n'
                        '   found.\n'
                        '\n'
                        "Note: These combinations don't yet list the amount you need of each food\n"
                        'in the combo to satisfy the diet problem.\n'
                        '\n'
                        'Project history\n'
                        '---------------\n'
                        '\n'
                        'Note: k-means and hierarchical clustering performed poorly on this data\n'
                        'because this data is highly dimensional (about 36 dimensions).\n'
                        '\n'
                        'Our previous attempts of combining foods used (ordered from newest to\n'
                        'older):\n'
                        '\n'
                        '-  Cluster the data and then use the average of each cluster as if they\n'
                        '   were food in our naive miner which does enumerate all possibilities\n'
                        '   of up to a given size (e.g. up to 5 foods in a single combo).\n'
                        '\n'
                        'Clustering algorithms used were:\n'
                        '`these <http://www.alglib.net/dataanalysis/clustering.php>`__, and an\n'
                        'ad-hoc method which turned out to be pretty bad.\n',
    'name': 'soylent-recipes',
    'package_data': {},
    'packages': ['soylent_recipes', 'soylent_recipes.tests'],
    'url': 'https://github.com/timdiels/soylent-recipes',
    'version': '0.0.0'}
)
