from setuptools import setup, find_packages

setup(
    name='utmist-gpu',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fog=utils.helper:main', 
        ],
    },
    install_requires=[
		'requests',
        'colorama',
        'python-dotenv'
    ],
    description='Description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jason Wang',
    author_email='jjh.wang@mail.utoronto.ca',
    url='https://github.com/wj-jason/utmist-gpu',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  
)

