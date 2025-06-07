# 设置镜像源（国内加速）
import os
# os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 登录HuggingFace（替换your_token）
from huggingface_hub import login
# login(token="xxx")

# 加载数据集
from datasets import load_dataset
# 按需选择：2023_all（全量）或分级（2023_level1/2/3）
ds = load_dataset("gaia-benchmark/GAIA", '2023_all', cache_dir="./cache", trust_remote_code=True)

# 查看数据集结构
print(ds['validation'][0])  # 验证集含答案，用于本地调试
print(ds['test'][0])        # 测试集无答案，仅提交结果

