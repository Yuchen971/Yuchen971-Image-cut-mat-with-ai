import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import shutil
from string import ascii_uppercase
import sys
import engine_lazy as engine
import splash_screen
import threading

def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    try:
        # PyInstaller 创建临时文件夹 _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("批量图像处理器")
        
        self.tab_control = ttk.Notebook(root)
        
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab1, text='自动截头')
        self.tab_control.add(self.tab2, text='自动抠图')
        
        self.tab_control.pack(expand=1, fill='both')
        
        self.create_tab1()
        self.create_tab2()
        
        # 加载人脸检测模型
        prototxt_path = resource_path('Face Detector Prototxt.prototxt')
        caffemodel_path = resource_path('Face Detection Model.caffemodel')
        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)

        # 加载 U2NET 模型
        # engine.load_model()
    
    def create_tab1(self):
        self.size_label = ttk.Label(self.tab1, text="目标尺寸 (宽 x 高)：")
        self.size_label.pack(pady=10)
        
        self.size_entry = ttk.Entry(self.tab1)
        self.size_entry.insert(0, "1350x1800")
        self.size_entry.pack(pady=10)
        
        self.dpi_label = ttk.Label(self.tab1, text="DPI (X, Y)：")
        self.dpi_label.pack(pady=10)
        
        self.dpi_entry = ttk.Entry(self.tab1)
        self.dpi_entry.insert(0, "300,300")
        self.dpi_entry.pack(pady=10)
        
        self.confidence_label = ttk.Label(self.tab1, text="置信度：")
        self.confidence_label.pack(pady=10)
        
        self.confidence_entry = ttk.Entry(self.tab1)
        self.confidence_entry.insert(0, "0.5")
        self.confidence_entry.pack(pady=10)
        
        self.percentage_label = ttk.Label(self.tab1, text="截取百分比：")
        self.percentage_label.pack(pady=10)
        
        self.percentage_entry = ttk.Entry(self.tab1)
        self.percentage_entry.insert(0, "70")
        self.percentage_entry.pack(pady=10)
        
        self.batch_button = ttk.Button(self.tab1, text="批量处理", command=self.batch_process)
        self.batch_button.pack(pady=10)
        
        self.single_button = ttk.Button(self.tab1, text="单个处理", command=self.single_process)
        self.single_button.pack(pady=10)
        
        self.image_label = ttk.Label(self.tab1)
        self.image_label.pack(pady=10)
        
        self.download_button = ttk.Button(self.tab1, text="下载", command=self.download_image, state=tk.DISABLED)
        self.download_button.pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(self.tab1, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.progress_bar.pack_forget()  # 初始时隐藏进度条
        
        self.progress_label = ttk.Label(self.tab1, text="")
        self.progress_label.pack(pady=5)
        self.progress_label.pack_forget()  # 初始时隐藏进度标签
    
    def create_tab2(self):
        self.size_label3 = ttk.Label(self.tab2, text="目标尺寸 (宽 x 高)：")
        self.size_label3.pack(pady=10)
        
        self.size_entry3 = ttk.Entry(self.tab2)
        self.size_entry3.insert(0, "1350x1800")
        self.size_entry3.pack(pady=10)
        
        self.dpi_label3 = ttk.Label(self.tab2, text="DPI (X, Y)：")
        self.dpi_label3.pack(pady=10)
        
        self.dpi_entry3 = ttk.Entry(self.tab2)
        self.dpi_entry3.insert(0, "300,300")
        self.dpi_entry3.pack(pady=10)
        
        self.batch_button3 = ttk.Button(self.tab2, text="批量处理", command=self.batch_process_matting)
        self.batch_button3.pack(pady=10)
        
        self.single_button3 = ttk.Button(self.tab2, text="单个处理", command=self.single_process_matting)
        self.single_button3.pack(pady=10)
        
        self.image_label3 = ttk.Label(self.tab2)
        self.image_label3.pack(pady=10)
        
        self.download_button3 = ttk.Button(self.tab2, text="下载", command=self.download_image_matting, state=tk.DISABLED)
        self.download_button3.pack(pady=10)
        
        self.progress_bar3 = ttk.Progressbar(self.tab2, orient="horizontal", length=300, mode="determinate")
        self.progress_bar3.pack(pady=10)
        self.progress_bar3.pack_forget()  # 初始时隐藏进度条
        
        self.progress_label3 = ttk.Label(self.tab2, text="")
        self.progress_label3.pack(pady=5)
        self.progress_label3.pack_forget()  # 初始时隐藏进度标签
    

    def batch_process(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
        
        size = self.size_entry.get().split('x')
        target_width, target_height = int(size[0]), int(size[1])
        dpi = tuple(map(int, self.dpi_entry.get().split(',')))
        confidence = float(self.confidence_entry.get())
        cut_percentage = float(self.percentage_entry.get()) / 100
        
        # 获取所有子文件夹中的图片文件
        image_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_files.append(os.path.join(root, file))
        
        total_files = len(image_files)
        
        # 创建进度条弹窗
        progress_window = tk.Toplevel(self.root)
        progress_window.title("处理进度")
        progress_window.geometry("300x100")
        
        progress_label = ttk.Label(progress_window, text="正在处理图片...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=250, mode="determinate")
        progress_bar.pack(pady=10)
        
        progress_bar["maximum"] = total_files
        progress_bar["value"] = 0
        
        for i, image_path in enumerate(image_files, 1):
            self.process_image(image_path, target_width, target_height, dpi, confidence, cut_percentage)
            
            progress_bar["value"] = i
            progress_label.config(text=f"处理进度: {i}/{total_files}")
            progress_window.update()
        
        progress_window.destroy()  # 关闭进度条弹窗
        messagebox.showinfo("成功", "批量处理完成")
    
    def single_process(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_path:
            return
        
        size = self.size_entry.get().split('x')
        target_width, target_height = int(size[0]), int(size[1])
        dpi = tuple(map(int, self.dpi_entry.get().split(',')))
        confidence = float(self.confidence_entry.get())
        cut_percentage = float(self.percentage_entry.get()) / 100
        
        processed_image = self.process_image(file_path, target_width, target_height, dpi, confidence, cut_percentage, display=True)
        
        # 移除了对 processed_image 是否为 None 的检查
        self.display_image(processed_image)
        self.download_button.config(state=tk.NORMAL)
        self.processed_image = processed_image

    def process_image(self, image_path, target_width, target_height, dpi, confidence, cut_percentage, display=False):
        img = cv2.imread(image_path)
        if img is None:
            print(f"错误：无法读取图像 {image_path}")
            return None

        (h, w) = img.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()

        face_detected = False
        cropped_img = img  # 默认使用整个图像
        
        for i in range(0, detections.shape[2]):
            conf = detections[0, 0, i, 2]
            if conf > confidence:
                face_detected = True
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                chin_y = startY + int(cut_percentage * (endY - startY))
                # 从下巴位置开始截取到图像底部
                cropped_img = img[chin_y:, :]
                break

        if not face_detected:
            print(f"警告：在图像 {image_path} 中未检测到人脸，使用原图")

        # 转换为 PIL 图像进行处理
        pil_image = Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))
        
        # 计算缩放比例，使用较大的比例以填满目标尺寸
        original_width, original_height = pil_image.size
        scale_w = target_width / original_width
        scale_h = target_height / original_height
        scale = max(scale_w, scale_h)  # 使用较大的缩放比例填满目标区域
        
        # 计算缩放后的尺寸
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # 缩放图像
        resized_img = pil_image.resize((new_width, new_height), Image.LANCZOS)
        
        # 计算裁剪位置（居中裁剪）
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        # 裁剪到目标尺寸
        final_img = resized_img.crop((left, top, right, bottom))
        
        if display:
            return final_img
        else:
            # 直接覆盖原始图像
            output_path = image_path
            final_img.save(output_path, 'JPEG', dpi=dpi, quality=100)
        return None
    
    def display_image(self, image):
        # 不使用 ImageTk，直接显示文本信息
        self.image_label.config(image="", text=f"图像处理完成\n尺寸: {image.width}x{image.height}")
    
    def download_image(self):
        if hasattr(self, 'processed_image'):
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if file_path:
                dpi = tuple(map(int, self.dpi_entry.get().split(',')))
                self.processed_image.save(file_path, 'JPEG', dpi=dpi, quality=95)
                messagebox.showinfo("成功", "图像已保存")
        else:
            messagebox.showerror("错误", "没有可下载的图像")
    
    def single_process_matting(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_path:
            return
        
        size = self.size_entry3.get().split('x')
        target_width, target_height = int(size[0]), int(size[1])
        dpi = tuple(map(int, self.dpi_entry3.get().split(',')))
        
        processed_image = self.process_image_matting(file_path, target_width, target_height, dpi, display=True)
        
        if processed_image:
            self.display_image_matting(processed_image)  # 使用适合抠图标签页的展示函数
            self.download_button3.config(state=tk.NORMAL)
            self.processed_image = processed_image
        else:
            messagebox.showerror("错误", "图像处理失败")

    def batch_process_matting(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
        
        size = self.size_entry3.get().split('x')
        target_width, target_height = int(size[0]), int(size[1])
        dpi = tuple(map(int, self.dpi_entry3.get().split(',')))
        
        image_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_files.append(os.path.join(root, file))
        
        total_files = len(image_files)
        
        progress_window = tk.Toplevel(self.root)
        progress_window.title("处理进度")
        progress_window.geometry("300x100")
        
        progress_label = ttk.Label(progress_window, text="正在处理图片...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=250, mode="determinate")
        progress_bar.pack(pady=10)
        
        progress_bar["maximum"] = total_files
        progress_bar["value"] = 0
        
        for i, image_path in enumerate(image_files, 1):
            self.process_image_matting(image_path, target_width, target_height, dpi)
            
            progress_bar["value"] = i
            progress_label.config(text=f"处理进度: {i}/{total_files}")
            progress_window.update()
        
        progress_window.destroy()
        messagebox.showinfo("成功", "批量处理完成")

    def process_image_matting(self, image_path, target_width, target_height, dpi, display=False):
        img = Image.open(image_path)
        if img is None:
            print(f"错误：无法读取图像 {image_path}")
            return None

        # 使用 remove_bg_mult 进行抠图
        processed_img = engine.remove_bg_mult(img)

        # 调整图像大小
        resized_img = processed_img.resize((target_width, target_height), Image.LANCZOS)
        
        if display:
            return resized_img
        else:
            # 始终覆盖原始图像
            output_path = image_path
            resized_img.save(output_path, 'JPEG', dpi=dpi, quality=95)
        return None

    def download_image_matting(self):
        if hasattr(self, 'processed_image'):
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if file_path:
                dpi = tuple(map(int, self.dpi_entry3.get().split(',')))
                self.processed_image.save(file_path, 'JPEG', dpi=dpi, quality=95)
                messagebox.showinfo("成功", "图像已保存")
        else:
            messagebox.showerror("错误", "没有可下载的图像")

    def display_image_matting(self, image):
        # 不使用 ImageTk，直接显示文本信息
        self.image_label3.config(image="", text=f"抠图处理完成\n尺寸: {image.width}x{image.height}")

    def process_single_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_path:
            return
        
        size = self.size_entry.get().split('x')
        target_width, target_height = int(size[0]), int(size[1])
        dpi = tuple(map(int, self.dpi_entry.get().split(',')))
        confidence = float(self.confidence_entry.get())
        cut_percentage = float(self.percentage_entry.get()) / 100
        
        # 处理图像，直接覆盖原图
        self.process_image(file_path, target_width, target_height, dpi, confidence, cut_percentage)
        
        # 显示处理完成的消息
        messagebox.showinfo("成功", "图像处理完成")
        
        # 读取处理后的图像并显示
        processed_img = Image.open(file_path)
        processed_img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(processed_img)
        
        # 创建新窗口显示结果
        result_window = tk.Toplevel(self.root)
        result_window.title("处理结果")
        
        # 创建 Label 来显示图像
        img_label = tk.Label(result_window, image=photo)
        img_label.image = photo  # 保持对图像的引用
        img_label.pack()
        
        # 添加文本说明
        tk.Label(result_window, text="处理完成！").pack()


def main():
    """主函数，简化启动流程"""
    # 创建主窗口
    root = tk.Tk()
    root.title("BatchCut - 正在启动...")
    root.geometry("400x200")
    
    # 居中显示
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # 创建启动信息
    status_label = tk.Label(root, text="正在启动 BatchCut...", font=('Arial', 14))
    status_label.pack(pady=50)
    
    progress_label = tk.Label(root, text="正在初始化组件...", font=('Arial', 10))
    progress_label.pack(pady=10)
    
    # 更新界面
    root.update()
    
    try:
        # 异步预加载模型
        progress_label.config(text="正在预加载模型...")
        root.update()
        model_thread = engine.preload_model_async()
        
        # 创建应用实例
        progress_label.config(text="正在加载界面...")
        root.update()
        
        # 清除启动界面
        for widget in root.winfo_children():
            widget.destroy()
        
        # 重新配置主窗口
        root.title("批量图像处理器")
        root.geometry("800x600")
        
        # 创建应用
        app = App(root)
        
        # 启动主循环
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("启动错误", f"应用启动失败: {str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()
