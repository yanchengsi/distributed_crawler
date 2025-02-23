# 在项目根目录创建setup.py
from setuptools import setup, find_packages


setup(
    name="distributed_crawler",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'mysql-connector-python',
        'requests',
        'redis'
    ]
)

