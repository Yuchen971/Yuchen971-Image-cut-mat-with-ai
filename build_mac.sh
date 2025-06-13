#!/bin/bash

# BatchCut Mac 应用构建脚本
# 使用 uv 和 PyInstaller 创建 Mac 应用

set -e  # 遇到错误时退出

echo "BatchCut Mac 应用构建工具"
echo "=========================="

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，请先安装 uv"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv 已安装"

# 检查必需的模型文件
required_files=(
    "auto_cut_and_mat_image/ckpt/u2net.pth"
    "auto_cut_and_mat_image/Face Detection Model.caffemodel"
    "auto_cut_and_mat_image/Face Detector Prototxt.prototxt"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "❌ 缺少必需的模型文件:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "请下载并放置这些文件后再运行打包脚本"
    exit 1
fi

echo "✅ 所有模型文件都存在"

# 清理旧的构建文件
echo ""
echo "清理旧的构建文件..."
rm -rf build dist __pycache__ BatchCut.spec

# 运行 Python 构建脚本
echo ""
echo "开始构建应用..."
python3 build_mac_app.py

echo ""
echo "构建完成！"
