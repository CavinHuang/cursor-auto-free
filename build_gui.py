import warnings
import os
import platform
import subprocess
import time
import threading
import shutil

# 忽略特定的SyntaxWarning
warnings.filterwarnings("ignore", category=SyntaxWarning, module="DrissionPage")

CURSOR_GUI_LOGO = """
   ╔══════════════════════════ Cursor GUI Packager ══════════════════════════╗
   ║                                                                         ║
   ║     📦 Package Builder & Deployment Tool                                ║
   ║                                                                         ║
   ║     ┌─────────────────┐      ╭─────────────────╮                       ║
   ║     │   Source Code   │  ──► │    Compiler     │                       ║
   ║     └─────────────────┘      ╰─────────────────╯                       ║
   ║            ▲                         │                                  ║
   ║            │                         ▼                                  ║
   ║     ┌─────────────────┐      ╭─────────────────╮                       ║
   ║     │   Resources     │      │   Executable    │                       ║
   ║     └─────────────────┘      ╰─────────────────╯                       ║
   ║            ▲                         │                                  ║
   ║            │                         ▼                                  ║
   ║     ┌─────────────────┐      ╭─────────────────╮      🚀              ║
   ║     │  Dependencies   │  ──► │    Packager     │ ──► Deploy           ║
   ║     └─────────────────┘      ╰─────────────────╯                       ║
   ║                                                                         ║
   ║     🔧 Build  📦 Package  🎯 Release  🖥️  Desktop  ▶️  Start           ║
   ║                                                                         ║
   ╚═════════════════════════════════════════════════════════════════════════╝
"""

class LoadingAnimation:
    def __init__(self):
        self.is_running = False
        self.animation_thread = None

    def start(self, message="Building"):
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate, args=(message,))
        self.animation_thread.start()

    def stop(self):
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        print("\r" + " " * 70 + "\r", end="", flush=True)

    def _animate(self, message):
        animation = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"  # 使用更现代的加载动画
        idx = 0
        while self.is_running:
            print(f"\r{message} {animation[idx % len(animation)]}", end="", flush=True)
            idx += 1
            time.sleep(0.1)

def print_logo():
    # 使用渐变色效果
    print("\033[38;5;32m" + CURSOR_GUI_LOGO + "\033[0m")  # 使用深蓝色
    print("\033[38;5;104m" + "Building Your Application with Style...".center(73) + "\033[0m\n")  # 使用淡紫色

def progress_bar(progress, total, prefix="", length=50):
    filled = int(length * progress // total)
    # 使用更现代的进度条样式
    bar = "█" * filled + "░" * (length - filled)
    percent = f"{100 * progress / total:.1f}"
    print(f"\r{prefix} |{bar}| {percent}% ", end="", flush=True)
    if progress == total:
        print("✓")  # 添加完成标记

def simulate_progress(message, duration=1.0, steps=20):
    print(f"\033[38;5;114m{message}\033[0m")  # 使用绿色
    for i in range(steps + 1):
        time.sleep(duration / steps)
        progress_bar(i, steps, prefix="Progress:", length=40)

def build_gui():
    # 清屏
    os.system("cls" if platform.system().lower() == "windows" else "clear")

    # 打印logo
    print_logo()

    system = platform.system().lower()
    spec_file = "CursorGUI.spec"

    # 创建输出目录
    output_dir = f"dist/{system if system != 'darwin' else 'mac'}"
    os.makedirs(output_dir, exist_ok=True)
    simulate_progress("创建输出目录...", 0.5)

    # 确保assets目录存在
    if not os.path.exists("assets"):
        os.makedirs("assets")
        simulate_progress("创建assets目录...", 0.5)

    # 运行PyInstaller
    pyinstaller_command = [
        "pyinstaller",
        spec_file,
        "--distpath",
        output_dir,
        "--workpath",
        f"build/{system}",
        "--noconfirm",
    ]

    loading = LoadingAnimation()
    try:
        simulate_progress("运行PyInstaller...", 2.0)
        loading.start("正在构建中")
        result = subprocess.run(pyinstaller_command, check=True, capture_output=True, text=True)
        loading.stop()

        if result.stderr:
            filtered_errors = [
                line for line in result.stderr.split("\n")
                if any(keyword in line.lower() for keyword in ["error:", "failed:", "completed", "directory:"])
            ]
            if filtered_errors:
                print("\033[93m构建警告/错误:\033[0m")
                print("\n".join(filtered_errors))

    except subprocess.CalledProcessError as e:
        loading.stop()
        print(f"\033[91m构建失败，错误代码 {e.returncode}\033[0m")
        if e.stderr:
            print("\033[91m错误详情:\033[0m")
            print(e.stderr)
        return
    except FileNotFoundError:
        loading.stop()
        print("\033[91m错误: 请确保已安装PyInstaller (pip install pyinstaller)\033[0m")
        return
    except KeyboardInterrupt:
        loading.stop()
        print("\n\033[91m构建被用户取消\033[0m")
        return
    finally:
        loading.stop()

    # 复制配置文件
    config_files = {
        "config.ini.example": "config.ini",
        ".env.example": ".env"
    }

    for src, dst in config_files.items():
        if os.path.exists(src):
            simulate_progress(f"复制配置文件 {src}...", 0.5)
            dst_path = os.path.join(output_dir, dst)
            shutil.copy2(src, dst_path)

    # 复制其他必要的资源文件
    if os.path.exists("assets"):
        simulate_progress("复制资源文件...", 0.5)
        assets_dst = os.path.join(output_dir, "assets")
        if os.path.exists(assets_dst):
            shutil.rmtree(assets_dst)
        shutil.copytree("assets", assets_dst)

    print(f"\n\033[92m构建成功完成! 输出目录: {output_dir}\033[0m")

if __name__ == "__main__":
    build_gui()