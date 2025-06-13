#!/usr/bin/env python3
"""
创建自动修复权限的启动器
"""

import os
import shutil

def create_launcher_script():
    """创建启动器脚本"""
    launcher_content = '''#!/bin/bash

# BatchCut 启动器 - 自动修复权限
APP_DIR="$(dirname "$0")"
APP_PATH="$(dirname "$APP_DIR")"
EXECUTABLE="$APP_DIR/BatchCut_Original"

# 检查是否需要修复权限
if [ ! -x "$EXECUTABLE" ]; then
    echo "正在修复应用权限..."
    
    # 尝试修复权限
    chmod +x "$EXECUTABLE" 2>/dev/null
    chmod -R 755 "$APP_PATH" 2>/dev/null
    
    if [ ! -x "$EXECUTABLE" ]; then
        # 如果普通权限修复失败，提示用户
        osascript -e 'display dialog "BatchCut 需要修复权限才能运行。\\n\\n请在终端中运行以下命令：\\n\\nchmod +x \\"'"$EXECUTABLE"'\\"\\nchmod -R 755 \\"'"$APP_PATH"'\\"\\n\\n或者右键点击应用选择\\"打开\\"" buttons {"确定"} default button "确定"'
        exit 1
    fi
fi

# 启动应用
exec "$EXECUTABLE" "$@"
'''
    
    return launcher_content

def create_auto_fix_launcher():
    """创建自动修复权限的启动器"""
    app_path = "dist/BatchCut.app"
    macos_path = f"{app_path}/Contents/MacOS"
    
    if not os.path.exists(app_path):
        print("❌ 应用不存在，请先构建应用")
        return False
    
    print("🔧 创建自动修复权限的启动器...")
    
    # 备份原始可执行文件
    original_exec = f"{macos_path}/BatchCut"
    backup_exec = f"{macos_path}/BatchCut_Original"
    
    if os.path.exists(original_exec):
        shutil.move(original_exec, backup_exec)
        print(f"✅ 备份原始可执行文件: {backup_exec}")
    
    # 创建新的启动器
    launcher_script = create_launcher_script()
    with open(original_exec, 'w') as f:
        f.write(launcher_script)
    
    # 给启动器执行权限
    os.chmod(original_exec, 0o755)
    os.chmod(backup_exec, 0o755)
    
    print(f"✅ 创建启动器: {original_exec}")
    return True

def create_simple_installer():
    """创建简单的安装脚本"""
    installer_content = '''#!/bin/bash

echo "BatchCut 简易安装程序"
echo "===================="

APP_NAME="BatchCut.app"
INSTALL_DIR="/Applications"

# 检查应用是否存在
if [ ! -d "$APP_NAME" ]; then
    echo "❌ 找不到 $APP_NAME"
    echo "请确保此脚本与 BatchCut.app 在同一目录中"
    exit 1
fi

echo "📦 正在安装 BatchCut 到应用程序文件夹..."

# 如果已存在，先删除
if [ -d "$INSTALL_DIR/$APP_NAME" ]; then
    echo "🗑️ 删除旧版本..."
    rm -rf "$INSTALL_DIR/$APP_NAME"
fi

# 复制到应用程序文件夹
if cp -R "$APP_NAME" "$INSTALL_DIR/"; then
    echo "✅ 应用已安装到 $INSTALL_DIR"
    
    # 修复权限
    chmod -R 755 "$INSTALL_DIR/$APP_NAME"
    chmod +x "$INSTALL_DIR/$APP_NAME/Contents/MacOS/"*
    
    echo "✅ 权限已修复"
    echo ""
    echo "🎉 安装完成！"
    echo ""
    echo "现在您可以："
    echo "1. 在启动台中找到 BatchCut"
    echo "2. 在应用程序文件夹中找到 BatchCut"
    echo "3. 直接双击运行"
    echo ""
    echo "首次运行可能需要在安全设置中允许运行"
    
    # 询问是否立即打开
    read -p "是否现在打开 BatchCut？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "$INSTALL_DIR/$APP_NAME"
    fi
else
    echo "❌ 安装失败"
    echo "请尝试手动将 $APP_NAME 拖拽到应用程序文件夹"
    echo "或使用管理员权限运行: sudo ./install.sh"
    exit 1
fi
'''
    
    with open('dist/install.sh', 'w') as f:
        f.write(installer_content)
    
    os.chmod('dist/install.sh', 0o755)
    print("✅ 创建安装脚本: dist/install.sh")

def create_user_guide():
    """创建用户指南"""
    guide_content = """# BatchCut 使用指南

## 快速安装

### 方法 1: 自动安装（推荐）
1. 双击 `install.sh` 
2. 按提示完成安装
3. 应用会自动安装到应用程序文件夹

### 方法 2: 手动安装
1. 将 `BatchCut.app` 拖到 `/Applications` 文件夹
2. 右键点击应用，选择"打开"

## 首次运行

如果遇到安全提示：
1. 系统偏好设置 > 安全性与隐私
2. 点击"仍要打开"

## 应用功能

### 自动截头
- 智能人脸识别
- 70% 位置截取（可调整）
- 输出 1350x1800 尺寸
- 无白边，不拉伸

### 自动抠图  
- AI 背景移除
- 高质量输出
- 批量处理支持

## 故障排除

### 权限问题
如果应用无法启动，在终端运行：
```bash
chmod -R 755 /Applications/BatchCut.app
chmod +x /Applications/BatchCut.app/Contents/MacOS/*
```

### 安全问题
1. 系统偏好设置 > 安全性与隐私
2. 允许从任何来源下载的应用
3. 或点击"仍要打开"

## 技术特性

- ✅ 无需 Python 环境
- ✅ M3 芯片优化
- ✅ 模型懒加载
- ✅ 快速启动
- ✅ 自动权限修复
"""
    
    with open('dist/使用指南.txt', 'w') as f:
        f.write(guide_content)
    
    print("✅ 创建使用指南: dist/使用指南.txt")

def main():
    """主函数"""
    print("BatchCut 启动器创建工具")
    print("=" * 30)
    
    # 创建自动修复权限的启动器
    if not create_auto_fix_launcher():
        return False
    
    # 创建安装脚本
    create_simple_installer()
    
    # 创建用户指南
    create_user_guide()
    
    print("\n🎉 启动器创建完成！")
    print("\n现在应用具有以下特性：")
    print("✅ 自动权限修复")
    print("✅ 智能启动器")
    print("✅ 简易安装脚本")
    print("✅ 详细使用指南")
    
    print("\n用户只需要：")
    print("1. 运行 install.sh 安装")
    print("2. 双击应用即可运行")
    print("3. 首次运行会自动修复权限")
    
    return True

if __name__ == '__main__':
    main()
