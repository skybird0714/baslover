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

class BlueArchiveCharacterFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("BAguesser反向查询 made by tkttn0714")
        self.root.geometry("1000x700")  # 增加窗口宽度
        self.root.resizable(True, True)
        
        # 设置图标 - 修改图标加载方式
        try:
            icon_path = self.resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
            else:
                print(f"图标文件不存在: {icon_path}")
                # 尝试查找可能的图标位置
                possible_paths = [
                    "icon.ico",
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico"),
                    os.path.join(os.path.dirname(sys.executable), "icon.ico")
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        print(f"尝试使用图标: {path}")
                        self.root.iconbitmap(default=path)
                        break
        except Exception as e:
            print(f"无法加载图标: {e}")
        
        # 加载角色数据
        self.load_character_data()
        
        # 创建界面
        self.create_ui()
        
        # 存储当前筛选结果
        self.current_results = []
        
        # 存储已下载的图片缓存
        self.image_cache = {}
        
    def resource_path(self, relative_path):
        """获取资源的绝对路径，适用于开发环境和PyInstaller打包后的环境"""
        try:
            # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        except Exception:
            # 如果不是通过PyInstaller打包，则使用当前文件夹
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
        
    def load_character_data(self):
        try:
            # 使用resource_path函数获取JSON文件的路径
            json_path = self.resource_path("characters.json")
            with open(json_path, "r", encoding="utf-8") as f:
                self.characters = json.load(f)
            print(f"成功加载 {len(self.characters)} 个角色")
        except Exception as e:
            messagebox.showerror("错误", f"无法加载角色数据: {e}")
            self.characters = {}
            
    def create_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧筛选条件面板
        filter_frame = ttk.LabelFrame(main_frame, text="筛选条件")
        filter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # 添加名称搜索框
        ttk.Label(filter_frame, text="角色名称:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        self.name_search_var = tk.StringVar()
        self.name_search_entry = ttk.Entry(filter_frame, textvariable=self.name_search_var, width=15)
        self.name_search_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=10)
        # 绑定回车键事件
        self.name_search_entry.bind("<Return>", self.search_by_name)
        
        # 添加名称搜索按钮
        ttk.Button(filter_frame, text="搜索名称", command=self.search_by_name).grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # 添加分隔线
        separator1 = ttk.Separator(filter_frame, orient='horizontal')
        separator1.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        # 获取所有可能的筛选条件值
        filter_options = self.get_filter_options()
        
        # 创建筛选条件控件
        self.filters = {}
        row = 3
        
        for category, values in filter_options.items():
            ttk.Label(filter_frame, text=f"{category}:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            
            # 使用Combobox作为筛选控件
            combobox = ttk.Combobox(filter_frame, width=15, state="readonly")
            combobox.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            
            # 添加一个空选项
            values = [""] + sorted(values)
            combobox["values"] = values
            combobox.current(0)
            
            # 绑定选择变更事件
            combobox.bind("<<ComboboxSelected>>", self.filter_characters)
            
            self.filters[category] = combobox
            row += 1
        
        # 添加重置按钮
        reset_button = ttk.Button(filter_frame, text="重置筛选", command=self.reset_filters)
        reset_button.grid(row=row, column=0, columnspan=2, padx=5, pady=10)
        row += 1
        
        # 添加分隔线
        separator = ttk.Separator(filter_frame, orient='horizontal')
        separator.grid(row=row, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        row += 1
        
        # 添加链接标签
        links = [
            ("开始游玩", "https://baguesser.071400.xyz/"),
            ("查看说明", "https://071400.xyz/2025/06/baguesser/"),
            ("作者", "https://space.bilibili.com/515626972/"),
            ("博客", "https://071400.xyz/")
        ]
        
        for text, url in links:
            link = ttk.Label(filter_frame, text=text, foreground="blue", cursor="hand2")
            link.grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
            link.bind("<Button-1>", lambda e, url=url: webbrowser.open_new(url))
            row += 1
        
        # 创建右侧结果显示面板
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建结果计数标签
        self.result_count_label = ttk.Label(result_frame, text="找到 0 个匹配角色")
        self.result_count_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # 创建结果列表框架
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建结果列表
        columns = ("ID", "名称", "学院", "社团", "武器类型", "稀有度", "攻击类型", "防御类型", "站位", "职能定位", "限定")
        self.result_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # 设置列标题和宽度
        for col in columns:
            self.result_tree.heading(col, text=col)
            if col == "ID":
                self.result_tree.column(col, width=40, anchor=tk.CENTER)
            elif col == "名称":
                self.result_tree.column(col, width=100, anchor=tk.W)
            elif col in ["学院", "社团"]:
                self.result_tree.column(col, width=120, anchor=tk.CENTER)
            else:
                self.result_tree.column(col, width=80, anchor=tk.CENTER)
        
        # 添加垂直滚动条（放在Treeview内部）
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=vsb.set)
        
        # 添加水平滚动条
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(xscrollcommand=hsb.set)
        
        # 放置Treeview和滚动条
        self.result_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # 配置grid权重，使Treeview可以随窗口调整大小
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定选择事件
        self.result_tree.bind("<<TreeviewSelect>>", self.show_character_details)
        
        # 创建角色详情面板
        details_frame = ttk.LabelFrame(result_frame, text="角色详情")
        details_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # 创建角色信息显示区域
        info_frame = ttk.Frame(details_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 角色头像
        self.character_image_label = ttk.Label(info_frame)
        self.character_image_label.grid(row=0, column=0, rowspan=6, padx=10, pady=5)
        
        # 角色详细信息
        self.character_name_label = ttk.Label(info_frame, text="", font=("", 12, "bold"))
        self.character_name_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.character_info_text = tk.Text(info_frame, width=40, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.character_info_text.grid(row=1, column=1, rowspan=5, sticky=tk.W, padx=5, pady=2)
        
        # 初始显示所有角色
        self.show_all_characters()
    
    def search_by_name(self, event=None):
        """根据名称搜索角色"""
        search_text = self.name_search_var.get().strip()
        if not search_text:
            # 如果搜索框为空，显示所有角色
            self.show_all_characters()
            return
            
        # 清空结果列表
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 搜索角色
        self.current_results = []
        for char_id, char_data in self.characters.items():
            name = char_data.get("name", "")
            if search_text.lower() in name.lower():
                self.current_results.append((char_id, char_data))
                
                # 添加到结果列表
                values = [
                    char_id,
                    char_data.get("name", ""),
                    char_data.get("学院", ""),
                    char_data.get("社团", ""),
                    char_data.get("武器类型", ""),
                    char_data.get("稀有度", ""),
                    char_data.get("攻击类型", ""),
                    char_data.get("防御类型", ""),
                    char_data.get("站位", ""),
                    char_data.get("职能定位", ""),
                    char_data.get("限定", "")
                ]
                self.result_tree.insert("", tk.END, values=values)
        
        # 更新结果计数
        self.result_count_label.config(text=f"找到 {len(self.current_results)} 个匹配角色")
        
        # 如果只有一个结果，自动选中并显示详情
        if len(self.current_results) == 1:
            self.result_tree.selection_set(self.result_tree.get_children()[0])
            self.show_character_details()
        else:
            # 清空详情显示
            self.clear_character_details()
    
    def get_filter_options(self):
        """从角色数据中提取所有可能的筛选选项"""
        options = {
            "学院": set(),
            "社团": set(),
            "武器类型": set(),
            "稀有度": set(),
            "攻击类型": set(),
            "防御类型": set(),
            "站位": set(),
            "职能定位": set(),
            "限定": set()
        }
        
        for char_id, char_data in self.characters.items():
            for category in options.keys():
                if category in char_data:
                    options[category].add(char_data[category])
        
        return options
    
    def filter_characters(self, event=None):
        """根据筛选条件过滤角色"""
        # 清空结果列表
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 获取筛选条件
        filters = {k: v.get() for k, v in self.filters.items() if v.get()}
        
        # 筛选角色
        self.current_results = []
        for char_id, char_data in self.characters.items():
            match = True
            for category, value in filters.items():
                if category in char_data and char_data[category] != value:
                    match = False
                    break
            
            if match:
                self.current_results.append((char_id, char_data))
                
                # 添加到结果列表
                values = [
                    char_id,
                    char_data.get("name", ""),
                    char_data.get("学院", ""),
                    char_data.get("社团", ""),
                    char_data.get("武器类型", ""),
                    char_data.get("稀有度", ""),
                    char_data.get("攻击类型", ""),
                    char_data.get("防御类型", ""),
                    char_data.get("站位", ""),
                    char_data.get("职能定位", ""),
                    char_data.get("限定", "")
                ]
                self.result_tree.insert("", tk.END, values=values)
        
        # 更新结果计数
        self.result_count_label.config(text=f"找到 {len(self.current_results)} 个匹配角色")
        
        # 清空详情显示
        self.clear_character_details()
    
    def reset_filters(self):
        """重置所有筛选条件"""
        # 清空名称搜索框
        self.name_search_var.set("")
        
        # 重置所有下拉框
        for combobox in self.filters.values():
            combobox.current(0)
        
        # 显示所有角色
        self.show_all_characters()
    
    def show_all_characters(self):
        """显示所有角色"""
        # 清空结果列表
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 添加所有角色到结果列表
        self.current_results = []
        for char_id, char_data in self.characters.items():
            self.current_results.append((char_id, char_data))
            
            values = [
                char_id,
                char_data.get("name", ""),
                char_data.get("学院", ""),
                char_data.get("社团", ""),
                char_data.get("武器类型", ""),
                char_data.get("稀有度", ""),
                char_data.get("攻击类型", ""),
                char_data.get("防御类型", ""),
                char_data.get("站位", ""),
                char_data.get("职能定位", ""),
                char_data.get("限定", "")
            ]
            self.result_tree.insert("", tk.END, values=values)
        
        # 更新结果计数
        self.result_count_label.config(text=f"找到 {len(self.current_results)} 个匹配角色")
        
        # 清空详情显示
        self.clear_character_details()
    
    def show_character_details(self, event=None):
        """显示选中角色的详细信息"""
        # 获取选中项
        selection = self.result_tree.selection()
        if not selection:
            return
        
        # 获取选中角色的索引
        item_id = selection[0]
        item_index = self.result_tree.index(item_id)
        
        if item_index < 0 or item_index >= len(self.current_results):
            return
        
        # 获取角色数据
        char_id, char_data = self.current_results[item_index]
        
        # 显示角色名称
        self.character_name_label.config(text=char_data.get("name", "未知"))
        
        # 显示角色详细信息
        self.character_info_text.config(state=tk.NORMAL)
        self.character_info_text.delete(1.0, tk.END)
        
        info_text = ""
        for key, value in char_data.items():
            if key not in ["name", "intro_link", "avatar_url"]:
                info_text += f"{key}: {value}\n"
        
        self.character_info_text.insert(tk.END, info_text)
        self.character_info_text.config(state=tk.DISABLED)
        
        # 显示角色头像
        avatar_url = char_data.get("avatar_url", "")
        if avatar_url:
            self.load_character_image(avatar_url)
        else:
            # 清除头像
            self.character_image_label.config(image="")
    
    def load_character_image(self, url):
        """异步加载角色头像"""
        if url in self.image_cache:
            # 使用缓存的图片
            self.character_image_label.config(image=self.image_cache[url])
            return
            
        # 清除当前图片
        self.character_image_label.config(image="")
        
        # 创建加载线程
        thread = threading.Thread(target=self._fetch_image, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _fetch_image(self, url):
        """在后台线程中获取图片"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 加载图片
                image = Image.open(BytesIO(response.content))
                
                # 调整大小
                image = image.resize((100, 100), Image.LANCZOS)
                
                # 转换为PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # 缓存图片
                self.image_cache[url] = photo
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.character_image_label.config(image=photo))
        except Exception as e:
            print(f"加载图片失败: {e}")
    
    def clear_character_details(self):
        """清空角色详情显示"""
        self.character_name_label.config(text="")
        self.character_info_text.config(state=tk.NORMAL)
        self.character_info_text.delete(1.0, tk.END)
        self.character_info_text.config(state=tk.DISABLED)
        self.character_image_label.config(image="")

def main():
    root = tk.Tk()
    app = BlueArchiveCharacterFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
