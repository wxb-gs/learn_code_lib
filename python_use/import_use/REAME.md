## python 导包最佳实践

| 导入方式       | 示例                           | 适用场景                   |
| ---------- | ---------------------------- | ---------------------- |
| ​**绝对导入**​ | `from pkg.subpkg import mod` | 推荐方式，明确路径层次            |
| ​**相对导入**​ | `from .sibling import func`  | 仅在包内部模块间使用， `..`作为上级目录 |
| ​**别名导入**​ | `import numpy as np`         | 解决命名冲突或简化长名称           |
| ​**按需导入**​ | `from module import obj`     | 减少内存占用，避免命名污染          |
按照绝对导入，设置包的**根目录**, 不受脚本执行位置影响
```python 
# 假如
pkg/
    subpkg/
        __init__.py
        xx.py
        core/
            __init__.py
            utils.py
```

```python
from pkg.subpkg.core import utils  # 导入整个模块
from pkg.subpkg.core.utils import func  # 导入特定函数/类
```
需确保项目根目录（`pkg`）在Python搜索路径中（可通过`sys.path`或环境变量设置）
```bash
export PYTHONPATH=/path/to/add
```
```python
import os
import sys

# 假设当前文件位于 pkg/subpkg/xx.py
current_dir = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在目录（subpkg）
root_dir = os.path.dirname(os.path.dirname(current_dir))  
if root_dir not in sys.path:
    sys.path.append(root_dir)
```