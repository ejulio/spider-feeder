from setuptools import setup, find_packages


setup(
    name='spider-feeder',
    version='0.2.0',
    url='https://github.com/ejulio/spider-feeder',
    author='Júlio César Batista',
    author_email='julio.batista@outlook.com',
    description='spider-feeder is a library to help loading inputs to scrapy spiders.',
    long_description='spider-feeder is a library to help loading inputs to scrapy spiders.',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['scrapy'],
    tests_require=['scrapy', 'pytest', 'pytest-mock'],
    extras_require={
        's3': ['botocore'],
        'collections': ['python-scrapinghub'],
        'pep8': ['flake8'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Scrapy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
