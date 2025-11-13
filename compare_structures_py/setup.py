"""
setup.py - compare_structures Python 包安装配置
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件（如果存在）
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="compare-structures",
    version="1.0.0",
    author="崔浩浩",
    author_email="",  # 可以添加邮箱
    description="增强版结构对比库 - 用于深度对比两个数据结构（字典/列表）",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/cuihaohao1220/compare_structures",
    packages=["compare_structures_py"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    install_requires=[
        "logzero>=1.7.0",
    ],
    keywords="compare, diff, structure, dictionary, list, comparison",
    project_urls={
        "Bug Reports": "https://github.com/cuihaohao1220/compare_structures/issues",
        "Source": "https://github.com/cuihaohao1220/compare_structures",
    },
)

