# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import customtkinter
import site
from pathlib import Path

# 获取customtkinter的资源目录路径
ctk_path = os.path.dirname(customtkinter.__file__)

# 查找fake_useragent数据文件路径
site_packages = site.getsitepackages()[0]
fake_ua_data_path = os.path.join(site_packages, 'fake_useragent', 'data')

# 根据操作系统选择图标
if sys.platform == 'darwin':
    icon = 'assets/icon.icns'
elif sys.platform == 'win32':
    icon = 'assets/icon.ico'
else:
    icon = 'assets/icon.png'

a = Analysis(
    ['run_gui.py'],  # 主文件
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # GUI资源文件目录
        ('config', 'config'),  # 配置文件目录
        ('gui', 'gui'),  # GUI模块目录
        (ctk_path, 'customtkinter'),  # 添加customtkinter资源
        ('.env', '.'),  # 添加.env环境变量文件
        ('names-dataset.txt', '.'),  # 添加姓名数据集文件
        ('turnstilePatch', 'turnstilePatch'),  # 添加turnstile插件目录
        (fake_ua_data_path, 'fake_useragent/data'),  # 添加fake_useragent数据文件
    ],
    hiddenimports=[
        'customtkinter',
        'darkdetect',
        'tkinter',
        'PIL',
        'PIL._tkinter_finder',
        'json',
        'logging',
        'requests',
        'dotenv',
        'fake_useragent',  # 确保包含fake-useragent库
        'fake_useragent.data',  # 添加fake_useragent.data模块
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# 添加额外的二进制文件
if sys.platform == 'darwin':
    a.binaries += [('libSystem.B.dylib', '/usr/lib/libSystem.B.dylib', 'BINARY')]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

if sys.platform == 'darwin':
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='CursorGUI',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # GUI应用
        disable_windowed_traceback=False,
        argv_emulation=False,  # macOS下设为False
        target_arch=None,
        #codesign_identity='Apple Development',  # 添加开发者签名
        #entitlements_file='entitlements.plist',  # 添加权限文件
        icon=icon
    )

    # 创建macOS应用程序包
    app = BUNDLE(
        exe,
        name='CursorGUI.app',
        icon=icon,
        bundle_identifier='com.cursor.gui',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.13.0',
            # 添加必要的权限声明
            'NSAppleEventsUsageDescription': 'This app needs to control system events.',
            'NSSystemAdministrationUsageDescription': 'This app needs system administration access.',
            'NSRequiresAquaSystemAppearance': 'False',  # 支持暗色模式
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='CursorGUI',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # GUI应用
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon
    )