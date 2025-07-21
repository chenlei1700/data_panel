@echo off
chcp 65001 >nul
title 股票仪表盘服务器管理工具

:menu
cls
echo ================================
echo 🚀 股票仪表盘服务器管理工具
echo ================================
echo.
echo 1. 启动多板块服务器 (默认配置)
echo 2. 启动多板块服务器 (高频更新模式)
echo 3. 启动多板块服务器 (低频更新模式)
echo 4. 启动多板块服务器 (禁用自动更新)
echo 5. 查看服务器状态
echo 6. 交互式配置
echo 7. 测试配置系统
echo 8. 查看配置模板
echo 9. 退出
echo.
set /p choice="请选择操作 (1-9): "

if "%choice%"=="1" goto start_default
if "%choice%"=="2" goto start_high_freq
if "%choice%"=="3" goto start_low_freq
if "%choice%"=="4" goto start_disabled
if "%choice%"=="5" goto show_status
if "%choice%"=="6" goto interactive_config
if "%choice%"=="7" goto test_system
if "%choice%"=="8" goto list_templates
if "%choice%"=="9" goto exit
goto menu

:start_default
cls
echo 🚀 启动多板块服务器 (默认配置)...
python server_launcher.py start --server multiplate
pause
goto menu

:start_high_freq
cls
echo 🚀 启动多板块服务器 (高频更新模式)...
python server_launcher.py start --server multiplate --config-template high_frequency
pause
goto menu

:start_low_freq
cls
echo 🚀 启动多板块服务器 (低频更新模式)...
python server_launcher.py start --server multiplate --config-template low_frequency
pause
goto menu

:start_disabled
cls
echo 🚀 启动多板块服务器 (禁用自动更新)...
python server_launcher.py start --server multiplate --config-template disabled
pause
goto menu

:show_status
cls
echo 📊 服务器状态
echo ================
python server_launcher.py status
echo.
pause
goto menu

:interactive_config
cls
echo ⚙️ 交互式配置
echo ================
python server_launcher.py config --interactive
pause
goto menu

:test_system
cls
echo 🧪 测试配置系统
echo ================
echo 注意: 这将测试配置文件功能，服务器API测试需要服务器运行
echo.
python test_auto_update_config.py --skip-server --skip-sse
echo.
pause
goto menu

:list_templates
cls
echo 📋 可用配置模板
echo ================
python server_launcher.py list-configs
echo.
pause
goto menu

:exit
echo 👋 感谢使用！
timeout /t 2 /nobreak >nul
exit
