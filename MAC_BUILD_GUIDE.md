# BatchCut Mac 应用打包指南

本指南将帮助你将 BatchCut 图像处理脚本打包成独立的 Mac 应用程序。

## 特性

✅ **无需 Python 环境** - 用户无需安装 Python 即可运行  
✅ **使用 uv 构建** - 快速、现代的 Python 包管理器  
✅ **模型懒加载** - 应用启动快速，模型按需加载  
✅ **启动画面** - 优雅的启动体验  
✅ **异步加载** - 后台预加载模型，不阻塞界面  

## 前置要求

### 1. 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 下载模型文件

你需要下载以下模型文件并放置到指定位置：

#### U2NET 模型（用于图像抠图）
- 下载地址: [u2net.pth](https://drive.google.com/file/d/1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ/view)
- 放置位置: `auto_cut_and_mat_image/ckpt/u2net.pth`

#### 人脸检测模型
- Caffemodel: [deploy.caffemodel](https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel)
- Prototxt: [deploy.prototxt](https://github.com/opencv/opencv/blob/master/samples/dnn/face_detector/deploy.prototxt)

重命名并放置：
- `auto_cut_and_mat_image/Face Detection Model.caffemodel`
- `auto_cut_and_mat_image/Face Detector Prototxt.prototxt`

## 构建步骤

### 方法 1: 使用简化脚本（推荐）

```bash
./build_mac.sh
```

### 方法 2: 使用 Python 脚本

```bash
python3 build_mac_app.py
```

### 方法 3: 手动构建

```bash
# 1. 安装依赖
uv sync

# 2. 运行 PyInstaller
uv run pyinstaller --clean BatchCut.spec
```

## 构建输出

成功构建后，你将在 `dist/` 目录下找到：

```
dist/
└── BatchCut.app/          # Mac 应用程序包
    ├── Contents/
    │   ├── MacOS/
    │   │   └── BatchCut    # 可执行文件
    │   ├── Resources/      # 资源文件
    │   └── Info.plist      # 应用信息
    └── ...
```

## 运行应用

### 直接运行
```bash
open dist/BatchCut.app
```

### 或者双击应用图标

## 优化特性说明

### 1. 懒加载模型
- **问题**: 原版应用启动时会立即加载所有模型，导致启动缓慢
- **解决**: 使用 `engine_lazy.py` 实现按需加载，只有在使用抠图功能时才加载 U2NET 模型

### 2. 启动画面
- **特性**: 显示优雅的启动画面，让用户知道应用正在启动
- **实现**: `splash_screen.py` 提供启动画面，显示加载进度

### 3. 异步预加载
- **特性**: 在后台异步预加载模型，不阻塞主界面
- **好处**: 用户可以立即使用其他功能，模型在后台静默加载

### 4. 独立运行
- **特性**: 打包后的应用包含所有依赖，无需用户安装 Python
- **实现**: PyInstaller 将 Python 解释器和所有依赖打包到应用中

## 故障排除

### 构建失败

1. **检查 uv 安装**
   ```bash
   uv --version
   ```

2. **检查模型文件**
   ```bash
   ls -la auto_cut_and_mat_image/ckpt/
   ls -la auto_cut_and_mat_image/Face*
   ```

3. **清理构建缓存**
   ```bash
   # 方法 1: 使用 Python 脚本清理
   python3 build_mac_app.py clean
   
   # 方法 2: 手动清理
   rm -rf build dist __pycache__ BatchCut.spec
   ```

### 应用启动失败

1. **检查控制台日志**
   ```bash
   open -a Console
   # 查找 BatchCut 相关错误
   ```

2. **在终端中运行**
   ```bash
   ./dist/BatchCut.app/Contents/MacOS/BatchCut
   ```

### 模型加载错误

1. **确认模型文件存在且完整**
2. **检查文件权限**
   ```bash
   chmod 644 auto_cut_and_mat_image/ckpt/u2net.pth
   chmod 644 auto_cut_and_mat_image/Face*
   ```

## 应用大小优化

构建的应用可能较大（500MB+），这是因为包含了：
- Python 解释器
- PyTorch 库
- OpenCV 库
- 模型文件

如需减小应用大小，可以考虑：
1. 使用 CPU 版本的 PyTorch
2. 移除不必要的依赖
3. 压缩模型文件

## 分发应用

### 代码签名（可选）
```bash
codesign --force --deep --sign "Developer ID Application: Your Name" dist/BatchCut.app
```

### 创建 DMG（可选）
```bash
hdiutil create -volname "BatchCut" -srcfolder dist/BatchCut.app -ov -format UDZO BatchCut.dmg
```

## 项目结构

```
batchcut_win/
├── auto_cut_and_mat_image/
│   ├── main.py              # 主应用文件（已优化）
│   ├── engine_lazy.py       # 懒加载引擎（新增）
│   ├── splash_screen.py     # 启动画面（新增）
│   ├── engine.py            # 原始引擎
│   ├── ckpt/
│   │   └── u2net.pth        # U2NET 模型
│   ├── Face Detection Model.caffemodel
│   └── Face Detector Prototxt.prototxt
├── pyproject.toml           # uv 项目配置（新增）
├── build_mac_app.py         # Python 构建脚本（新增）
├── build_mac.sh             # Shell 构建脚本（新增）
└── MAC_BUILD_GUIDE.md       # 本文档（新增）
```

## 技术细节

### 懒加载实现
- 使用线程锁确保模型只加载一次
- 双重检查锁定模式避免竞态条件
- 异步预加载提升用户体验

### 启动优化
- 启动画面立即显示，给用户反馈
- 主窗口在后台初始化
- 模型在后台异步加载

### 打包优化
- 使用 PyInstaller 的 BUNDLE 模式创建 .app 包
- 自动包含所有必需的数据文件
- 隐藏导入确保所有依赖被包含

## 支持

如果遇到问题，请检查：
1. 模型文件是否正确下载和放置
2. uv 是否正确安装
3. 系统是否有足够的磁盘空间（至少 2GB）
4. macOS 版本兼容性（建议 macOS 10.14+）
