@echo off
echo ========================================
echo 股票仪表盘系统 - 一键启动脚本
echo ========================================
echo.

:: 检查 Python 环境
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python 环境
    echo 请确保已安装 Python 并添加到系统 PATH
    pause
    exit /b 1
)
echo ✅ Python 环境检查通过

:: 检查依赖包
echo [2/4] 检查 Python 依赖包...
python -c "import flask, pandas, plotly" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告: 缺少必要的 Python 包
    echo 正在安装依赖包...
    pip install flask flask-cors pandas plotly numpy
)
echo ✅ 依赖包检查完成

:: 启动后端服务
echo [3/4] 启动后端API服务...

start "演示仪表盘 (端口5004)" cmd /k "echo 启动演示仪表盘服务... && python api/show_plate_server_v2.py 5004"
timeout /t 2 >nul

echo ✅ 后端服务启动完成

:: 启动前端服务
echo [4/4] 启动前端服务...
echo.
echo 🚀 正在启动前端开发服务器...
echo 📱 浏览器将自动打开 http://localhost:8081
echo.
echo ⚠️  注意: 请等待几秒钟让所有服务完全启动
echo 💡 如需停止服务，请关闭所有终端窗口
echo.

:: 启动前端 (在当前窗口)
npm run serve

pause