from setuptools import setup, find_packages

setup(
    name="chatbot",
    version="0.1.0",
    # 关键配置：声明包位置和结构
    package_dir={"": "src"},              # 指定代码根目录为 src
    packages=find_packages(where="src"),  # 自动发现所有包（含子包）
)