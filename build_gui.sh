#!/bin/bash

# 设置环境变量以忽略警告
export PYTHONWARNINGS=ignore::SyntaxWarning:DrissionPage

echo "正在创建虚拟环境..."

# 清理旧的构建文件
if [ -d "build" ]; then
    echo "清理旧的构建文件..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "清理旧的发布文件..."
    rm -rf dist
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境失败!"
        exit 1
    fi
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# 确保PyInstaller是最新版本
pip install --upgrade pyinstaller

# 检查必要的文件是否存在
if [ ! -f "run_gui.py" ]; then
    echo "错误: run_gui.py 文件不存在!"
    exit 1
fi

# 检查必要的目录
for dir in "assets" "config" "gui"; do
    if [ ! -d "$dir" ]; then
        echo "创建 $dir 目录..."
        mkdir "$dir"
    fi
done

# 运行构建脚本
echo "开始构建过程..."
python build_gui.py

# 检查构建是否成功
if [ $? -ne 0 ]; then
    echo "构建失败!"
    exit 1
fi

# 检查输出文件
output_file="dist/mac/CursorGUI"
if [ ! -f "$output_file" ]; then
    echo "错误: 构建文件不存在: $output_file"
    exit 1
fi

# 设置可执行权限（仅在macOS/Linux上）
if [ "$(uname)" == "Darwin" ] || [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    echo "设置可执行权限..."
    chmod +x "$output_file"
fi

echo "构建完成!"
echo "输出文件: $output_file"