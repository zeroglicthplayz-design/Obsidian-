from setuptools import setup, find_packages

setup(
    name='obsidian-marketplace-bot',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'discord.py>=2.3.0',
        'python-dotenv>=1.0.0',
        'Flask>=3.0.0',
    ],
    python_requires='>=3.11',
)
