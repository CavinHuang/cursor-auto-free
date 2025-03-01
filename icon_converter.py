#!/usr/bin/env python3
import os
import sys
import shutil
from PIL import Image
import cairosvg

class IconConverter:
    def __init__(self):
        self.temp_dir = 'assets/temp'
        self.assets_dir = 'assets'
        self.ensure_directories()

    def ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.temp_dir, self.assets_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def cleanup(self):
        """清理临时文件"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def svg_to_png(self, svg_path, size=(1024, 1024)):
        """将SVG转换为PNG"""
        png_path = os.path.join(self.temp_dir, 'icon.png')
        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            output_width=size[0],
            output_height=size[1]
        )
        return png_path

    def create_icns(self, png_path):
        """创建macOS图标（.icns）"""
        icns_path = os.path.join(self.assets_dir, 'icon.icns')
        if sys.platform == 'darwin':
            os.system(f'sips -s format icns "{png_path}" --out "{icns_path}"')
        return icns_path

    def create_ico(self, png_path):
        """创建Windows图标（.ico）"""
        ico_path = os.path.join(self.assets_dir, 'icon.ico')
        img = Image.open(png_path)
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64),
                     (128, 128), (256, 256)]
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        return ico_path

    def create_png_icon(self, png_path):
        """创建PNG图标（用于Linux）"""
        output_path = os.path.join(self.assets_dir, 'icon.png')
        shutil.copy2(png_path, output_path)
        return output_path

    def convert(self, svg_path):
        """转换SVG到所有需要的图标格式"""
        try:
            # 检查SVG文件是否存在
            if not os.path.exists(svg_path):
                raise FileNotFoundError(f"找不到SVG文件: {svg_path}")

            # 转换为PNG
            print("正在将SVG转换为PNG...")
            png_path = self.svg_to_png(svg_path)

            # 根据操作系统创建相应格式的图标
            if sys.platform == 'darwin':
                print("正在创建macOS图标（.icns）...")
                icon_path = self.create_icns(png_path)
            elif sys.platform == 'win32':
                print("正在创建Windows图标（.ico）...")
                icon_path = self.create_ico(png_path)
            else:
                print("正在创建Linux图标（.png）...")
                icon_path = self.create_png_icon(png_path)

            print(f"图标创建成功: {icon_path}")
            return icon_path

        except Exception as e:
            print(f"转换过程中出错: {str(e)}")
            raise
        finally:
            self.cleanup()

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python icon_converter.py <svg文件路径>")
        sys.exit(1)

    svg_path = sys.argv[1]
    converter = IconConverter()

    try:
        icon_path = converter.convert(svg_path)
        print(f"转换完成！输出文件: {icon_path}")
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()