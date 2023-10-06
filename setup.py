from setuptools import setup, find_packages

setup(
    name='singular',
    version='0.1',
    author='Gunnar Thorsteinsson',
    author_email='gunnar.thorsteinsson@columbia.edu',
    description='One battery analysis interface to rule them all',
    long_description='Now I am driving the bus!',
    url='https://github.com/steingartlab/singular',
    packages=find_packages(),  # Automatically find and include all packages
    install_requires=[
        'galvani',
        'numpy',
        'pandas',
        'pytest'
        'Requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)