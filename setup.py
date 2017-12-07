from setuptools import setup, find_packages

setup(
    name='polo-withdraw',
    version='1.0',
    author='Evan Klitzke',
    author_email='evan@eklitzke.org',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'polo-withdraw = polowithdraw:main',
        ]
    }
)
