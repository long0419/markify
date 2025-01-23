from setuptools import setup, find_packages

setup(
    name="markify",
    version="0.1.0",
    packages=find_packages(include=['markify*']),
    package_dir={'markify': 'markify'},
    entry_points={
        'console_scripts': [
            'markitdown=markify.main:main', 
        ],
    },
    install_requires=[
        # 依赖列表可以从requirements.txt获取
    ],
)
