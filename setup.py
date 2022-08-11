from setuptools import setup 

setup(
    name = 'echodeletes',
    version = '0.0.1',
    author = 'James Walder',
    author_email = 'james.walder@stfc.ac.uk',
    description = 'Deletion requests',
    long_description = 'file: README.md',
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/snafus/echodeletes.git',
    project_urls ={'Bug Tracker':'https://github.com/snafus/echodeletes/issues'},
    classifiers =['Programming Language :: Python :: 3','License :: OSI Approved :: MIT License'],
    packages = ['echodeletes'],
    python_requires = '>=3.6',
    install_requires = ['fastapi', 'sqlalchemy', 'pydantic', 'psycopg2-binary', 'python-dotenv'],
    scripts = ['echodeletes/xrdrep.py'],
)