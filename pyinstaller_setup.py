"""
使用PyInstaller打包BAguesser反向查询工具
"""

import PyInstaller.__main__
import os
import sys

# 确保图标文件存在
icon_path = "icon.ico"
if not os.path.exists(icon_path):
    print(f"警告: 图标文件 {icon_path} 不存在!")
    sys.exit(1)

# 使用PyInstaller打包
PyInstaller.__main__.run([
    'baslover.py',                    # 主程序文件
    '--name=BAguesser反向查询',        # 应用名称
    '--onefile',                      # 打包成单个EXE文件
    '--windowed',                     # 使用Windows GUI模式，不显示控制台
    '--icon=icon.ico',                # 设置图标
    '--add-data=characters.json;.',   # 添加数据文件
    '--add-data=icon.ico;.',          # 添加图标文件
    '--clean',                        # 清理临时文件
    '--noconfirm',                    # 不确认覆盖
]) 