from setuptools import setup, find_packages

setup(
    name='fog',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fog = fog.__main__:main',
        ],
    },
    install_requires=[
		'python-dotenv',
		'requests',
		'colorama',
    ],
)
