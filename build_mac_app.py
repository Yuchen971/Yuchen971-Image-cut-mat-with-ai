#!/usr/bin/env python3
"""
Mac 应用打包脚本
使用 uv 和 PyInstaller 创建 Mac 应用
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并处理错误"""
    print(f"执行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False

def check_uv():
    """检查 uv 是否安装"""
    try:
        subprocess.run(['uv', '--version'], check=True, capture_output=True)
        print("✓ uv 已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ uv 未安装，请先安装 uv")
        print("安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def check_model_files():
    """检查必需的模型文件"""
    required_files = [
        "auto_cut_and_mat_image/ckpt/u2net.pth",
        "auto_cut_and_mat_image/Face Detection Model.caffemodel",
        "auto_cut_and_mat_image/Face Detector Prototxt.prototxt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("✗ 缺少必需的模型文件:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\n请下载并放置这些文件后再运行打包脚本")
        return False
    
    print("✓ 所有模型文件都存在")
    return True

def create_pyinstaller_spec():
    """创建 PyInstaller spec 文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['auto_cut_and_mat_image/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('auto_cut_and_mat_image/ckpt', 'ckpt'),
        ('auto_cut_and_mat_image/Face Detection Model.caffemodel', '.'),
        ('auto_cut_and_mat_image/Face Detector Prototxt.prototxt', '.'),
        ('auto_cut_and_mat_image/u2net', 'u2net'),
    ],
    hiddenimports=[
        'torch',
        'torchvision',
        'cv2',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL._tkinter_finder',
        'PIL._imagingtk',
        'numpy',
        'scikit-image',
        'skimage',
        'skimage.transform',
        'skimage.io',
        'skimage.color',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.constants',
        'tkinter.font',
        '_tkinter',
        '_imagingtk',
        'auto_cut_and_mat_image.engine_lazy',
        'auto_cut_and_mat_image.splash_screen',
        'auto_cut_and_mat_image.u2net.model',
        'auto_cut_and_mat_image.u2net.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BatchCut',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BatchCut',
)

app = BUNDLE(
    coll,
    name='BatchCut.app',
    icon='auto_cut_and_mat_image/app_icon.ico',
    bundle_identifier='com.batchcut.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Image',
                'CFBundleTypeIconFile': 'app_icon.ico',
                'LSItemContentTypes': ['public.image'],
                'LSHandlerRank': 'Owner'
            }
        ]
    },
)
'''
    
    with open('BatchCut.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ 创建了 PyInstaller spec 文件")

def build_app():
    """构建 Mac 应用"""
    print("开始构建 Mac 应用...")
    
    # 检查前置条件
    if not check_uv():
        return False
    
    if not check_model_files():
        return False
    
    # 创建虚拟环境并安装依赖
    print("\n1. 创建虚拟环境并安装依赖...")
    if not run_command(['uv', 'sync']):
        return False
    
    # 清理旧的构建文件
    print("\n2. 清理旧的构建文件...")
    clean_build()
    
    # 创建 PyInstaller spec 文件
    print("\n3. 创建 PyInstaller 配置...")
    create_pyinstaller_spec()
    
    # 使用 uv 运行 PyInstaller
    print("\n4. 使用 PyInstaller 构建应用...")
    if not run_command(['uv', 'run', 'pyinstaller', '--clean', '--noconfirm', 'BatchCut.spec']):
        return False
    
    # 检查构建结果
    app_path = Path('dist/BatchCut.app')
    if app_path.exists():
        print(f"\n✓ 应用构建成功!")
        print(f"应用位置: {app_path.absolute()}")
        
        # 显示应用大小
        try:
            size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
            size_mb = size / (1024 * 1024)
            print(f"应用大小: {size_mb:.1f} MB")
        except:
            pass
        
        print("\n使用方法:")
        print(f"1. 双击 {app_path} 启动应用")
        print("2. 或者在终端中运行: open dist/BatchCut.app")
        
        return True
    else:
        print("\n✗ 应用构建失败")
        return False

def clean_build():
    """清理构建文件"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['BatchCut.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ 清理目录: {dir_name}")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"✓ 清理文件: {file_name}")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        print("清理构建文件...")
        clean_build()
        return
    
    print("BatchCut Mac 应用构建工具")
    print("=" * 40)
    
    if build_app():
        print("\n🎉 构建完成!")
    else:
        print("\n❌ 构建失败!")
        sys.exit(1)

if __name__ == '__main__':
    main()
