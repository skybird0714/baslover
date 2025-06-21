import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import webbrowser

# 创建一个临时图标文件
def create_temp_icon():
    try:
        # 如果icon.ico不存在，创建一个简单的图标
        if not os.path.exists("icon.ico"):
            print("创建临时图标文件...")
            # 使用tkinter创建一个简单的图标
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 创建一个画布
            canvas = tk.Canvas(root, width=32, height=32)
            canvas.create_oval(4, 4, 28, 28, fill="blue", outline="")
            canvas.create_text(16, 16, text="BA", fill="white", font=("Arial", 10, "bold"))
            
            # 保存为临时图标
            canvas.postscript(file="temp_icon.ps", colormode="color")
            
            # 使用PIL将PostScript转换为ICO
            from PIL import Image, ImageTk
            img = Image.open("temp_icon.ps")
            img.save("icon.ico")
            
            # 清理临时文件
            os.remove("temp_icon.ps")
            print("临时图标已创建: icon.ico")
            
            root.destroy()
            return True
    except Exception as e:
        print(f"创建临时图标失败: {e}")
    return False

# 主函数
if __name__ == "__main__":
    # 检查图标文件是否存在，如果不存在则创建
    if not os.path.exists("icon.ico"):
        created = create_temp_icon()
        if created:
            print("已创建临时图标，现在可以运行打包脚本了")
        else:
            print("无法创建图标文件，程序将使用默认图标")
    else:
        print("图标文件已存在，可以继续打包")
    
    print("\n请运行以下命令之一进行打包:")
    print("python pyinstaller_setup.py")
    print("或")
    print("python setup.py build") 