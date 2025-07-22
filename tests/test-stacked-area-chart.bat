@echo off
REM 堆叠面积图组件快速测试脚本
REM 用于快速启动和测试新增的堆叠面积图功能

echo.
echo ========================================
echo  📊 堆叠面积图组件快速测试
echo ========================================
echo.

echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo 🔍 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装或不在PATH中
    pause
    exit /b 1
)
echo ✅ Node.js环境正常

echo.
echo 🔍 检查项目依赖...
if not exist node_modules (
    echo 📦 安装前端依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ 前端依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ 前端依赖已安装

echo.
echo 🎯 选择测试模式:
echo 1. 启动完整演示环境 (推荐)
echo 2. 仅运行堆叠面积图演示脚本
echo 3. 启动演示服务器 (端口5004)
echo 4. 启动前端开发服务器 (端口8081)
echo 5. 查看项目结构
echo 6. 退出

echo.
set /p choice=请输入选项 (1-6): 

if "%choice%"=="1" goto full_demo
if "%choice%"=="2" goto script_demo
if "%choice%"=="3" goto backend_only
if "%choice%"=="4" goto frontend_only
if "%choice%"=="5" goto show_structure
if "%choice%"=="6" goto end

echo ❌ 无效选项，请重新选择
pause
goto start

:full_demo
echo.
echo 🚀 启动完整演示环境...
echo.
echo 📋 将会启动:
echo   - 演示API服务器 (端口5004)
echo   - 前端开发服务器 (端口8081)
echo   - 浏览器将自动打开演示页面
echo.
echo ⏳ 正在启动服务器...

REM 启动后端服务器
start "API服务器" cmd /k "echo 🌐 启动API服务器... && python api/show_plate_server_demo.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端服务器
start "前端服务器" cmd /k "echo 🎨 启动前端服务器... && npm run serve"

echo.
echo ✅ 服务器正在启动中...
echo.
echo 📖 使用指南:
echo   1. 等待约30秒让服务器完全启动
echo   2. 浏览器会自动打开主页 (http://localhost:8081)
echo   3. 点击 "堆叠面积图演示" 卡片查看新功能
echo   4. 或直接访问: http://localhost:8081/stacked-area-demo
echo.
echo 🔧 如需停止服务器，请关闭对应的命令行窗口
echo.

REM 等待一段时间后打开浏览器
timeout /t 8 /nobreak >nul
start http://localhost:8081/stacked-area-demo

echo 🎉 演示环境已启动完成！
pause
goto end

:script_demo
echo.
echo 📊 运行堆叠面积图演示脚本...
echo.
python scripts/demo-stacked-area-chart.py
pause
goto start

:backend_only
echo.
echo 🌐 启动演示API服务器 (端口5004)...
echo.
echo 🔗 API端点:
echo   - http://localhost:5004/health
echo   - http://localhost:5004/api/chart-data/stacked-area-demo
echo   - http://localhost:5004/api-diagnostic.html
echo.
python api/show_plate_server_demo.py
pause
goto end

:frontend_only
echo.
echo 🎨 启动前端开发服务器 (端口8081)...
echo.
echo 🔗 访问地址:
echo   - http://localhost:8081 (主页)
echo   - http://localhost:8081/stacked-area-demo (堆叠面积图演示)
echo.
npm run serve
pause
goto end

:show_structure
echo.
echo 📁 堆叠面积图相关文件结构:
echo.
echo 📦 前端组件:
echo   📄 src/components/dashboard/StackedAreaChartComponent.vue
echo   📄 src/components/dashboard/ComponentRenderer.vue
echo   📄 src/views/StackedAreaDemo.vue
echo   📄 src/router/index.js
echo   📄 src/views/Home.vue
echo.
echo 📦 后端API:
echo   📄 api/show_plate_server_demo.py
echo   📄 api/show_plate_server_multiplate_v2.py
echo.
echo 📦 文档和工具:
echo   📄 docs/STACKED_AREA_CHART_GUIDE.md
echo   📄 scripts/demo-stacked-area-chart.py
echo   📄 STACKED_AREA_CHART_UPDATE.md
echo.
echo 📦 配置文件:
echo   📄 .vscode/tasks.json
echo.
pause
goto start

:start
goto full_demo

:end
echo.
echo 👋 感谢使用堆叠面积图组件演示！
echo.
echo 📚 更多信息:
echo   - 使用指南: docs/STACKED_AREA_CHART_GUIDE.md
echo   - 更新摘要: STACKED_AREA_CHART_UPDATE.md
echo   - 项目主页: http://localhost:8081
echo.
pause
