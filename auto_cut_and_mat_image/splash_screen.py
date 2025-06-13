import tkinter as tk
from tkinter import ttk
import threading
import time

class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BatchCut")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # 居中显示
        self.center_window()
        
        # 移除窗口装饰
        self.root.overrideredirect(True)
        
        # 设置背景色
        self.root.configure(bg='#f0f0f0')
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=40, pady=40)
        main_frame.pack(fill='both', expand=True)
        
        # 应用标题
        title_label = tk.Label(
            main_frame, 
            text="BatchCut", 
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(20, 10))
        
        # 副标题
        subtitle_label = tk.Label(
            main_frame, 
            text="批量图像处理器", 
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#666666'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # 状态标签
        self.status_label = tk.Label(
            main_frame, 
            text="正在启动应用...", 
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#888888'
        )
        self.status_label.pack(pady=(0, 20))
        
        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, 
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=(0, 20))
        self.progress.start(10)
        
        # 版本信息
        version_label = tk.Label(
            main_frame, 
            text="版本 1.0.0", 
            font=('Arial', 8),
            bg='#f0f0f0',
            fg='#aaaaaa'
        )
        version_label.pack(side='bottom')
        
        # 设置窗口置顶
        self.root.attributes('-topmost', True)
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.config(text=message)
        self.root.update()
    
    def close(self):
        """关闭启动画面"""
        self.progress.stop()
        self.root.destroy()
    
    def show(self):
        """显示启动画面"""
        self.root.update()
        return self.root

def show_splash_screen():
    """显示启动画面并返回控制对象"""
    splash = SplashScreen()
    return splash

if __name__ == "__main__":
    # 测试启动画面
    splash = show_splash_screen()
    
    # 模拟加载过程
    for i, message in enumerate([
        "正在启动应用...",
        "正在加载界面...",
        "正在初始化组件...",
        "启动完成"
    ]):
        splash.update_status(message)
        time.sleep(1)
    
    splash.close()
