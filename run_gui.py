#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui import main

if __name__ == "__main__":
    main()