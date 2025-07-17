# -*- coding: utf-8 -*-
"""
脚本工具包初始化文件
Scripts Package Initialization

包含项目管理和自动化脚本：
- 配置生成器 (auto-config-generator.py)
- 环境检查 (check-environment.py)
- 初始化配置 (init-config.py)
- 快速添加页面 (quick-add-page.py)
- 性能监控 (performance-monitor.py)
- 质量检查 (quality-check.py)

Author: chenlei
"""

__version__ = "1.0.0"
__author__ = "chenlei"

# 脚本包的常量配置
SCRIPTS_DIR = __file__.replace("__init__.py", "")
PROJECT_ROOT = SCRIPTS_DIR.replace("scripts/", "").replace("scripts\\", "")

__all__ = [
    "SCRIPTS_DIR",
    "PROJECT_ROOT",
]
