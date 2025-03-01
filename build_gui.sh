#!/bin/bash

# 设置环境变量以忽略警告
export PYTHONWARNINGS=ignore::SyntaxWarning:DrissionPage

# 获取操作系统类型
OS_TYPE=$(uname)

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

# 检查并创建必要的目录
for dir in "assets" "config" "gui"; do
    if [ ! -d "$dir" ]; then
        echo "创建 $dir 目录..."
        mkdir "$dir"
    fi
done

# 运行PyInstaller
echo "开始构建过程..."
if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS构建
    pyinstaller CursorGUI.spec --clean --noconfirm

    # 检查.app文件是否创建成功
    if [ ! -d "dist/CursorGUI.app" ]; then
        echo "错误: 构建失败，没有生成.app文件"
        exit 1
    fi

    # 设置权限
    chmod -R 755 "dist/CursorGUI.app"

    echo "构建完成!"
    echo "应用程序包位置: dist/CursorGUI.app"

    # 可选：创建DMG文件
    if command -v create-dmg &> /dev/null; then
        echo "创建DMG安装包..."
        create-dmg \
            --volname "CursorGUI" \
            --volicon "assets/icon.icns" \
            --window-pos 200 120 \
            --window-size 800 400 \
            --icon-size 100 \
            --icon "CursorGUI.app" 200 190 \
            --hide-extension "CursorGUI.app" \
            --app-drop-link 600 185 \
            "dist/CursorGUI.dmg" \
            "dist/CursorGUI.app"
        echo "DMG安装包已创建: dist/CursorGUI.dmg"
    fi
else
    # Linux/其他系统构建
    pyinstaller CursorGUI.spec --clean --noconfirm

    # 检查可执行文件是否创建成功
    if [ ! -f "dist/CursorGUI" ]; then
        echo "错误: 构建失败，没有生成可执行文件"
        exit 1
    fi

    # 设置权限
    chmod +x "dist/CursorGUI"

    echo "构建完成!"
    echo "可执行文件位置: dist/CursorGUI"
fi

# 创建发布包
VERSION="1.0.0"
RELEASE_DIR="dist/release"
mkdir -p "$RELEASE_DIR"

if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS发布包
    if [ -f "dist/CursorGUI.dmg" ]; then
        cp "dist/CursorGUI.dmg" "$RELEASE_DIR/CursorGUI-${VERSION}-mac.dmg"
    else
        tar -czf "$RELEASE_DIR/CursorGUI-${VERSION}-mac.tar.gz" -C dist CursorGUI.app
    fi
else
    # Linux/其他系统发布包
    tar -czf "$RELEASE_DIR/CursorGUI-${VERSION}-linux.tar.gz" -C dist CursorGUI
fi

echo "发布包已创建: $RELEASE_DIR"