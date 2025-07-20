#!/bin/bash

echo "========================================"
echo "股票仪表盘系统 - 一键启动脚本 (Linux/Mac)"
echo "========================================"
echo

# 检查 Python 环境
echo "[1/4] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 环境"
    echo "请确保已安装 Python 3"
    exit 1
fi
echo "✅ Python 环境检查通过"

# 检查依赖包
echo "[2/4] 检查 Python 依赖包..."
python3 -c "import flask, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  警告: 缺少必要的 Python 包"
    echo "正在安装依赖包..."
    pip3 install flask flask-cors pandas plotly numpy
fi
echo "✅ 依赖包检查完成"

# 启动后端服务
echo "[3/4] 启动后端API服务..."

# 启动演示仪表盘服务
gnome-terminal --title="演示仪表盘 (端口5004)" -- bash -c "echo '启动演示仪表盘服务...'; python3 api/show_plate_server_multiplate_v2.py; exec bash" &
sleep 2

# 启动堆叠面积图演示服务
gnome-terminal --title="堆叠面积图演示 (端口5007)" -- bash -c "echo '启动堆叠面积图演示服务...'; python3 api/stacked_area_demo_server.py; exec bash" &
sleep 2

echo "✅ 后端服务启动完成"

# 启动前端服务
echo "[4/4] 启动前端服务..."
echo
echo "🚀 正在启动前端开发服务器..."
echo "📱 浏览器将自动打开 http://localhost:8081"
echo
echo "⚠️  注意: 请等待几秒钟让所有服务完全启动"
echo "💡 如需停止服务，请关闭所有终端窗口"
echo

# 启动前端
npm run serve