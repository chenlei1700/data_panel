#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量检查脚本 - 统一的代码质量检查工具
Code Quality Check Script - Unified code quality checking tool

Author: chenlei
"""

import subprocess
import sys
import os
from pathlib import Path
import json
import time


class CodeQualityChecker:
    """代码质量检查器"""
    
    def __init__(self, project_root=None):
        """初始化"""
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.results = {}
        self.overall_score = 0
        
    def run_command(self, command, description):
        """运行命令并记录结果"""
        print(f"🔍 {description}...")
        try:
            result = subprocess.run(
                command, 
                cwd=self.project_root, 
                capture_output=True, 
                text=True,
                shell=True
            )
            
            success = result.returncode == 0
            self.results[description] = {
                'success': success,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': command
            }
            
            if success:
                print(f"✅ {description} - 通过")
            else:
                print(f"❌ {description} - 失败")
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}...")
            
            return success
            
        except Exception as e:
            print(f"💥 {description} - 执行异常: {e}")
            self.results[description] = {
                'success': False,
                'error': str(e),
                'command': command
            }
            return False
    
    def check_python_syntax(self):
        """检查Python语法"""
        print("\n📝 Python代码检查")
        print("=" * 40)
        
        score = 0
        total = 0
        
        # 语法检查
        total += 1
        if self.run_command("python -m py_compile api/*.py", "Python语法检查"):
            score += 1
        
        # Flake8代码风格检查
        total += 1
        if self.run_command("flake8 api/ scripts/ --statistics", "Flake8代码风格检查"):
            score += 1
        
        # Black代码格式检查
        total += 1
        if self.run_command("black --check api/ scripts/", "Black代码格式检查"):
            score += 1
        
        # isort导入排序检查
        total += 1
        if self.run_command("isort --check-only api/ scripts/", "导入排序检查"):
            score += 1
        
        python_score = (score / total) * 100 if total > 0 else 0
        print(f"\n📊 Python代码质量得分: {python_score:.1f}% ({score}/{total})")
        
        return python_score
    
    def check_javascript_syntax(self):
        """检查JavaScript/Vue语法"""
        print("\n🟨 JavaScript/Vue代码检查")
        print("=" * 40)
        
        score = 0
        total = 0
        
        # Vue/JS Lint检查
        total += 1
        if self.run_command("npm run lint", "Vue/JavaScript Lint检查"):
            score += 1
        
        js_score = (score / total) * 100 if total > 0 else 0
        print(f"\n📊 JavaScript/Vue代码质量得分: {js_score:.1f}% ({score}/{total})")
        
        return js_score
    
    def check_dependencies(self):
        """检查依赖安全性"""
        print("\n🔒 依赖安全检查")
        print("=" * 40)
        
        score = 0
        total = 0
        
        # Python依赖安全检查 (如果安装了safety)
        total += 1
        try:
            if subprocess.run(["safety", "--version"], capture_output=True).returncode == 0:
                if self.run_command("safety check", "Python依赖安全检查"):
                    score += 1
            else:
                print("⚠️  Safety未安装，跳过Python依赖安全检查")
                total -= 1
        except:
            print("⚠️  Safety检查失败，跳过")
            total -= 1
        
        # NPM依赖审计
        total += 1
        if self.run_command("npm audit --audit-level=moderate", "NPM依赖安全检查"):
            score += 1
        
        deps_score = (score / total) * 100 if total > 0 else 100
        print(f"\n📊 依赖安全得分: {deps_score:.1f}% ({score}/{total})")
        
        return deps_score
    
    def check_test_coverage(self):
        """检查测试覆盖率"""
        print("\n🧪 测试覆盖率检查")
        print("=" * 40)
        
        score = 0
        total = 0
        
        # Python测试覆盖率
        total += 1
        if self.run_command("python -m pytest tests/ --cov=api --cov-report=term-missing", "Python测试覆盖率"):
            score += 1
        
        # JavaScript测试覆盖率 (如果配置了)
        if (self.project_root / "jest.config.js").exists():
            total += 1
            if self.run_command("npm run test:coverage", "JavaScript测试覆盖率"):
                score += 1
        
        test_score = (score / total) * 100 if total > 0 else 0
        print(f"\n📊 测试覆盖率得分: {test_score:.1f}% ({score}/{total})")
        
        return test_score
    
    def check_documentation(self):
        """检查文档质量"""
        print("\n📚 文档质量检查")
        print("=" * 40)
        
        score = 0
        total = 0
        
        # 检查必要文档是否存在
        required_docs = [
            "README.md",
            "docs/README.md", 
            "CONTRIBUTORS.md",
            "requirements.txt",
            "package.json"
        ]
        
        for doc in required_docs:
            total += 1
            doc_path = self.project_root / doc
            if doc_path.exists() and doc_path.stat().st_size > 100:
                print(f"✅ {doc} - 存在且内容充足")
                score += 1
            else:
                print(f"❌ {doc} - 缺失或内容不足")
        
        # 检查API文档注释覆盖率
        total += 1
        api_files = list((self.project_root / "api").glob("*.py"))
        documented_files = 0
        
        for api_file in api_files:
            if api_file.name.startswith("__"):
                continue
            content = api_file.read_text(encoding='utf-8')
            if '"""' in content and 'Author:' in content:
                documented_files += 1
        
        if len(api_files) > 0:
            doc_coverage = documented_files / len(api_files)
            if doc_coverage >= 0.8:
                print(f"✅ API文档覆盖率 - {doc_coverage:.1%}")
                score += 1
            else:
                print(f"❌ API文档覆盖率不足 - {doc_coverage:.1%}")
        
        doc_score = (score / total) * 100 if total > 0 else 0
        print(f"\n📊 文档质量得分: {doc_score:.1f}% ({score}/{total})")
        
        return doc_score
    
    def check_project_structure(self):
        """检查项目结构"""
        print("\n📁 项目结构检查")
        print("=" * 40)
        
        score = 0
        total = 0
        
        # 检查关键目录结构
        required_structure = {
            "api/": "后端API目录",
            "src/": "前端源码目录", 
            "docs/": "文档目录",
            "scripts/": "脚本目录",
            "tests/": "测试目录",
            ".vscode/": "VS Code配置目录"
        }
        
        for path, description in required_structure.items():
            total += 1
            if (self.project_root / path).exists():
                print(f"✅ {path} - {description}")
                score += 1
            else:
                print(f"❌ {path} - {description} (缺失)")
        
        # 检查配置文件
        config_files = {
            "project-config.json": "项目配置文件",
            ".vscode/tasks.json": "VS Code任务配置",
            "docker-compose.yml": "Docker Compose配置",
            "requirements.txt": "Python依赖文件",
            "package.json": "Node.js配置文件"
        }
        
        for file, description in config_files.items():
            total += 1
            if (self.project_root / file).exists():
                print(f"✅ {file} - {description}")
                score += 1
            else:
                print(f"❌ {file} - {description} (缺失)")
        
        structure_score = (score / total) * 100 if total > 0 else 0
        print(f"\n📊 项目结构得分: {structure_score:.1f}% ({score}/{total})")
        
        return structure_score
    
    def generate_report(self):
        """生成质量检查报告"""
        print("\n📋 代码质量检查报告")
        print("=" * 50)
        
        # 运行所有检查
        python_score = self.check_python_syntax()
        js_score = self.check_javascript_syntax()
        deps_score = self.check_dependencies()
        test_score = self.check_test_coverage()
        doc_score = self.check_documentation()
        structure_score = self.check_project_structure()
        
        # 计算总体得分
        scores = [python_score, js_score, deps_score, test_score, doc_score, structure_score]
        valid_scores = [s for s in scores if s >= 0]
        overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        # 输出总结
        print(f"\n🎯 总体质量得分: {overall_score:.1f}%")
        print("\n📊 详细分数:")
        print(f"   Python代码质量: {python_score:.1f}%")
        print(f"   JavaScript代码质量: {js_score:.1f}%")
        print(f"   依赖安全性: {deps_score:.1f}%")
        print(f"   测试覆盖率: {test_score:.1f}%")
        print(f"   文档质量: {doc_score:.1f}%")
        print(f"   项目结构: {structure_score:.1f}%")
        
        # 等级评定
        if overall_score >= 90:
            grade = "A+ (优秀)"
            color = "🟢"
        elif overall_score >= 80:
            grade = "A (良好)"
            color = "🟡"
        elif overall_score >= 70:
            grade = "B (合格)"
            color = "🟠"
        else:
            grade = "C (需改进)"
            color = "🔴"
        
        print(f"\n{color} 代码质量等级: {grade}")
        
        # 保存详细报告
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"quality_report_{timestamp}.json"
        
        report_data = {
            'timestamp': timestamp,
            'overall_score': overall_score,
            'grade': grade,
            'scores': {
                'python': python_score,
                'javascript': js_score,
                'dependencies': deps_score,
                'test_coverage': test_score,
                'documentation': doc_score,
                'project_structure': structure_score
            },
            'details': self.results
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 详细报告已保存到: {report_file}")
        except Exception as e:
            print(f"⚠️  保存报告失败: {e}")
        
        return overall_score
    
    def suggest_improvements(self):
        """提供改进建议"""
        print(f"\n💡 改进建议:")
        
        suggestions = []
        
        # 基于检查结果提供建议
        for check, result in self.results.items():
            if not result['success']:
                if 'Flake8' in check:
                    suggestions.append("• 运行 'flake8 api/ scripts/' 查看具体的代码风格问题")
                    suggestions.append("• 使用 'black api/ scripts/' 自动格式化代码")
                elif 'Black' in check:
                    suggestions.append("• 运行 'black api/ scripts/' 自动格式化代码")
                elif 'isort' in check:
                    suggestions.append("• 运行 'isort api/ scripts/' 自动排序导入")
                elif 'test' in check.lower():
                    suggestions.append("• 增加单元测试覆盖率，目标覆盖率 >80%")
                elif 'npm' in check:
                    suggestions.append("• 运行 'npm run lint:fix' 自动修复前端代码问题")
        
        # 通用建议
        suggestions.extend([
            "• 定期运行 'python scripts/quality-check.py' 进行质量检查",
            "• 使用 'pre-commit' 钩子确保提交前代码质量",
            "• 保持文档和代码同步更新",
            "• 定期更新依赖包以修复安全漏洞"
        ])
        
        for suggestion in suggestions[:8]:  # 限制显示数量
            print(suggestion)


def main():
    """主函数"""
    print("🔍 代码质量检查工具")
    print("=" * 50)
    print()
    
    checker = CodeQualityChecker()
    
    try:
        overall_score = checker.generate_report()
        checker.suggest_improvements()
        
        print(f"\n✅ 质量检查完成，总体得分: {overall_score:.1f}%")
        
        # 返回适当的退出码
        if overall_score >= 80:
            return 0  # 成功
        elif overall_score >= 70:
            return 1  # 警告
        else:
            return 2  # 需要改进
            
    except KeyboardInterrupt:
        print("\n⚠️  检查被用户中断")
        return 3
    except Exception as e:
        print(f"\n❌ 检查执行失败: {e}")
        return 4


if __name__ == "__main__":
    sys.exit(main())
