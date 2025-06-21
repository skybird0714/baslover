import sys
from cx_Freeze import setup, Executable

# 依赖项
build_exe_options = {
    "packages": ["tkinter", "PIL", "requests", "json", "io", "threading", "webbrowser"],
    "include_files": [
        "characters.json",  # 包含角色数据
        "icon.ico",         # 包含图标
    ],
    "excludes": ["matplotlib", "numpy", "pandas", "scipy"],
}

# 基本信息
setup(
    name="BAslover v1.1",
    version="1.0",
    description="蔚蓝档案人物反向查询工具",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "baslover.py",
            base="Win32GUI",  # 使用Windows GUI模式，不显示控制台
            icon="icon.ico",  # 设置图标
            target_name="BAslover v1.1.exe"  # 生成的EXE文件名
        )
    ]
) 