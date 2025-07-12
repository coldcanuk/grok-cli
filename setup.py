from setuptools import setup, find_packages

setup(
    name='grok-cli',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'grok-cli = grok_cli.cli:main'
        ]
    },
    author='Grok Assisted Build',
    description='A CLI for xAI Grok API, functional in Windows PowerShell',
    long_description='Provides interactive chat, single prompts, and vision support using Grok API. Get API key at https://x.ai/api.',
)
