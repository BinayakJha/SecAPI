from setuptools import setup, find_packages

setup(
    name='sentinelai',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'cryptography>=41.0.0'
    ],
    entry_points={
        'console_scripts': [
            'sentinel=sentinel.cli:main',  # 👈 Enables CLI command
        ],
    },
    author='Binayak Jha',
    description='Secure, intelligent API key management and CLI agent.',
    keywords='security api keys encryption cli sentinel',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
