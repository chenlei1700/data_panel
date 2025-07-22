#!/bin/bash

# 堆叠面积图组件快速测试脚本
# 用于快速启动和测试新增的堆叠面积图功能

echo ""
echo "========================================"
echo " 📊 堆叠面积图组件快速测试"
echo "========================================"
echo ""

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python未安装或不在PATH中"
    exit 1
fi

# 尝试使用python3，如果不存在则使用python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "✅ Python环境正常 ($($PYTHON_CMD --version))"

# 检查Node.js环境
echo ""
echo "🔍 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装或不在PATH中"
    exit 1
fi
echo "✅ Node.js环境正常 ($(node --version))"

# 检查项目依赖
echo ""
echo "🔍 检查项目依赖..."
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 前端依赖安装失败"
        exit 1
    fi
fi
echo "✅ 前端依赖已安装"

# 主菜单函数
show_menu() {
    echo ""
    echo "🎯 选择测试模式:"
    echo "1. 启动完整演示环境 (推荐)"
    echo "2. 仅运行堆叠面积图演示脚本"
    echo "3. 启动演示服务器 (端口5004)"
    echo "4. 启动前端开发服务器 (端口8081)"
    echo "5. 查看项目结构"
    echo "6. 退出"
    echo ""
}

# 完整演示环境
full_demo() {
    echo ""
    echo "🚀 启动完整演示环境..."
    echo ""
    echo "📋 将会启动:"
    echo "   - 演示API服务器 (端口5004)"
    echo "   - 前端开发服务器 (端口8081)"
    echo "   - 浏览器将自动打开演示页面"
    echo ""
    echo "⏳ 正在启动服务器..."

    # 启动后端服务器（后台运行）
    echo "🌐 启动API服务器..."
    $PYTHON_CMD api/show_plate_server_demo.py &
    BACKEND_PID=$!
    
    # 等待后端启动
    sleep 3
    
    # 启动前端服务器（后台运行）
    echo "🎨 启动前端服务器..."
    npm run serve &
    FRONTEND_PID=$!
    
    echo ""
    echo "✅ 服务器正在启动中..."
    echo ""
    echo "📖 使用指南:"
    echo "   1. 等待约30秒让服务器完全启动"
    echo "   2. 手动访问主页: http://localhost:8081"
    echo "   3. 点击 \"堆叠面积图演示\" 卡片查看新功能"
    echo "   4. 或直接访问: http://localhost:8081/stacked-area-demo"
    echo ""
    echo "🔧 按 Ctrl+C 停止所有服务器"
    
    # 等待一段时间后尝试打开浏览器
    sleep 8
    if command -v open &> /dev/null; then
        # macOS
        open http://localhost:8081/stacked-area-demo
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open http://localhost:8081/stacked-area-demo
    else
        echo "🌐 请手动打开浏览器访问: http://localhost:8081/stacked-area-demo"
    fi
    
    echo "🎉 演示环境已启动完成！按 Ctrl+C 停止服务器"
    
    # 创建cleanup函数
    cleanup() {
        echo ""
        echo "🛑 正在停止服务器..."
        kill $BACKEND_PID 2>/dev/null
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ 服务器已停止"
        exit 0
    }
    
    # 设置信号处理
    trap cleanup SIGINT SIGTERM
    
    # 等待用户中断
    wait
}

# 脚本演示
script_demo() {
    echo ""
    echo "📊 运行堆叠面积图演示脚本..."
    echo ""
    $PYTHON_CMD scripts/demo-stacked-area-chart.py
    read -p "按Enter键继续..."
}

# 仅启动后端
backend_only() {
    echo ""
    echo "🌐 启动演示API服务器 (端口5004)..."
    echo ""
    echo "🔗 API端点:"
    echo "   - http://localhost:5004/health"
    echo "   - http://localhost:5004/api/chart-data/stacked-area-demo"
    echo "   - http://localhost:5004/api-diagnostic.html"
    echo ""
    $PYTHON_CMD api/show_plate_server_demo.py
}

# 仅启动前端
frontend_only() {
    echo ""
    echo "🎨 启动前端开发服务器 (端口8081)..."
    echo ""
    echo "🔗 访问地址:"
    echo "   - http://localhost:8081 (主页)"
    echo "   - http://localhost:8081/stacked-area-demo (堆叠面积图演示)"
    echo ""
    npm run serve
}

# 显示项目结构
show_structure() {
    echo ""
    echo "📁 堆叠面积图相关文件结构:"
    echo ""
    echo "📦 前端组件:"
    echo "   📄 src/components/dashboard/StackedAreaChartComponent.vue"
    echo "   📄 src/components/dashboard/ComponentRenderer.vue"
    echo "   📄 src/views/StackedAreaDemo.vue"
    echo "   📄 src/router/index.js"
    echo "   📄 src/views/Home.vue"
    echo ""
    echo "📦 后端API:"
    echo "   📄 api/show_plate_server_demo.py"
    echo "   📄 api/show_plate_server_multiplate_v2.py"
    echo ""
    echo "📦 文档和工具:"
    echo "   📄 docs/STACKED_AREA_CHART_GUIDE.md"
    echo "   📄 scripts/demo-stacked-area-chart.py"
    echo "   📄 STACKED_AREA_CHART_UPDATE.md"
    echo ""
    echo "📦 配置文件:"
    echo "   📄 .vscode/tasks.json"
    echo ""
    read -p "按Enter键继续..."
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (1-6): " choice
    
    case $choice in
        1)
            full_demo
            break
            ;;
        2)
            script_demo
            ;;
        3)
            backend_only
            break
            ;;
        4)
            frontend_only
            break
            ;;
        5)
            show_structure
            ;;
        6)
            echo ""
            echo "👋 感谢使用堆叠面积图组件演示！"
            echo ""
            echo "📚 更多信息:"
            echo "   - 使用指南: docs/STACKED_AREA_CHART_GUIDE.md"
            echo "   - 更新摘要: STACKED_AREA_CHART_UPDATE.md"
            echo "   - 项目主页: http://localhost:8081"
            echo ""
            exit 0
            ;;
        *)
            echo "❌ 无效选项，请重新选择"
            ;;
    esac
done
