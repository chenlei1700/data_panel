#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.gitignore 检查脚本
检查 .gitignore 文件是否正确工作

Author: chenlei
"""

import os
import subprocess
import sys
from pathlib import Path

def check_gitignore():
    """检查 .gitignore 文件是否正确工作"""
    print("🔍 检查 .gitignore 文件...")
    
    # 检查 .gitignore 文件是否存在
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("❌ .gitignore 文件不存在")
        return False
    
    # 检查应该被忽略的文件和目录
    ignored_items = [
        "node_modules/",
        "__pycache__/",
        "*.pyc",
        "dist/",
        "backup/",
        ".vscode/settings.json",
        ".env",
        "project-config.backup.*.json"
    ]
    
    print("✅ .gitignore 文件存在")
    
    # 检查关键忽略规则
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing_rules = []
    for item in ignored_items:
        if item not in content:
            missing_rules.append(item)
    
    if missing_rules:
        print(f"⚠️  以下规则可能缺失: {', '.join(missing_rules)}")
    else:
        print("✅ 关键忽略规则都存在")
    
    # 检查当前 git 状态
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            untracked = [line for line in result.stdout.strip().split('\n') 
                        if line.startswith('??')]
            ignored = [line for line in result.stdout.strip().split('\n') 
                      if line.startswith('!!')]
            
            print(f"📊 当前状态: {len(untracked)} 个未跟踪文件")
            if ignored:
                print(f"🚫 {len(ignored)} 个文件被忽略")
            
            # 检查是否有应该被忽略的文件没有被忽略
            problematic_files = []
            for line in untracked:
                filename = line[3:].strip()
                if (filename.endswith('.pyc') or 
                    filename.endswith('.log') or 
                    '__pycache__' in filename or
                    filename.startswith('node_modules/')):
                    problematic_files.append(filename)
            
            if problematic_files:
                print(f"⚠️  以下文件应该被忽略但没有被忽略: {', '.join(problematic_files)}")
            else:
                print("✅ 没有发现应该被忽略但未被忽略的文件")
        
    except FileNotFoundError:
        print("⚠️  git 命令不可用，无法检查 git 状态")
    
    return True

if __name__ == "__main__":
    check_gitignore()
