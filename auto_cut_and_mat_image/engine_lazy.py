import numpy as np
from PIL import Image
import torch
from torchvision import transforms
from u2net import utils, model
import os
import threading

# 全局变量存储模型
_model_pred = None
_model_lock = threading.Lock()
_model_loading = False

def get_model_path():
    """获取模型文件路径"""
    return os.path.join(os.path.dirname(__file__), 'ckpt', 'u2net.pth')

def load_model():
    """懒加载模型"""
    global _model_pred, _model_loading
    
    if _model_pred is not None:
        return _model_pred
    
    with _model_lock:
        # 双重检查锁定
        if _model_pred is not None:
            return _model_pred
            
        if _model_loading:
            # 如果正在加载，等待加载完成
            while _model_loading:
                threading.Event().wait(0.1)
            return _model_pred
        
        _model_loading = True
        try:
            print("正在加载 U2NET 模型...")
            model_path = get_model_path()
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"模型文件不存在: {model_path}")
            
            _model_pred = model.U2NET(3, 1)
            _model_pred.load_state_dict(torch.load(model_path, map_location="cpu"))
            _model_pred.eval()
            print("U2NET 模型加载完成")
            return _model_pred
        finally:
            _model_loading = False

def norm_pred(d):
    ma = torch.max(d)
    mi = torch.min(d)
    dn = (d - mi) / (ma - mi)
    return dn

def preprocess(image):
    label_3 = np.zeros(image.shape)
    label = np.zeros(label_3.shape[0:2])

    if 3 == len(label_3.shape):
        label = label_3[:, :, 0]
    elif 2 == len(label_3.shape):
        label = label_3

    if 3 == len(image.shape) and 2 == len(label.shape):
        label = label[:, :, np.newaxis]
    elif 2 == len(image.shape) and 2 == len(label.shape):
        image = image[:, :, np.newaxis]
        label = label[:, :, np.newaxis]

    transform = transforms.Compose([utils.RescaleT(320), utils.ToTensorLab(flag=0)])
    sample = transform({"imidx": np.array([0]), "image": image, "label": label})

    return sample

def remove_bg(image, resize=False):
    model_pred = load_model()  # 懒加载模型
    sample = preprocess(np.array(image))

    with torch.no_grad():
        inputs_test = torch.FloatTensor(sample["image"].unsqueeze(0).float())

        d1, _, _, _, _, _, _ = model_pred(inputs_test)
        pred = d1[:, 0, :, :]
        predict = norm_pred(pred).squeeze().cpu().detach().numpy()
        img_out = Image.fromarray(predict * 255).convert("RGB")
        img_out = img_out.resize((image.size), resample=Image.BILINEAR)
        empty_img = Image.new("RGBA", (image.size), 0)
        img_out = Image.composite(image, empty_img, img_out.convert("L"))
        del d1, pred, predict, inputs_test, sample

        return img_out

def _remove(image):
    model_pred = load_model()  # 懒加载模型
    sample = preprocess(np.array(image))
    with torch.no_grad():
        inputs_test = torch.FloatTensor(sample["image"].unsqueeze(0).float())
        d1, _, _, _, _, _, _ = model_pred(inputs_test)
        pred = d1[:, 0, :, :]
        predict = norm_pred(pred).squeeze().cpu().detach().numpy()
        mask = Image.fromarray((predict * 255).astype(np.uint8), mode='L')
        mask = mask.resize(image.size, Image.LANCZOS)
        
        # 创建 RGBA 图像
        img_out = Image.new('RGBA', image.size, (0, 0, 0, 0))
        img_out.paste(image, (0, 0), mask)

    return img_out

def remove_bg_mult(image):
    # 保存原始图像大小
    original_size = image.size
    
    # 将图像调整到合适的大小进行处理
    process_size = (512, 512)
    img_for_process = image.copy().resize(process_size, Image.LANCZOS)
    
    img_out = img_for_process.copy()
    for _ in range(4):
        img_out = _remove(img_out)
    
    # 创建白色背景，使用原始图像大小
    white_background = Image.new("RGBA", original_size, (255, 255, 255, 255))
    
    # 将抠图结果调整回原始大小
    img_out = img_out.resize(original_size, Image.LANCZOS)
    
    # 创建一个遮罩
    mask = img_out.split()[3]
    
    # 使用原始图像和遮罩创建最终结果
    final_img = Image.composite(image, white_background, mask)
    
    return final_img.convert("RGB")

def change_background(image, background):
    background = background.resize((image.size), resample=Image.BILINEAR)
    img_out = Image.alpha_composite(background, image)
    return img_out

def is_model_loaded():
    """检查模型是否已加载"""
    return _model_pred is not None

def preload_model_async():
    """异步预加载模型"""
    def _load():
        load_model()
    
    thread = threading.Thread(target=_load, daemon=True)
    thread.start()
    return thread
