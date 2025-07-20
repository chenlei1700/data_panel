#!/usr/bin/env python3
"""
堆叠面积图组件集成验证脚本
验证新组件是否正确集成到项目中

使用方法:
python scripts/validate-stacked-area-integration.py
"""

import os
import json
import re
import sys
from pathlib import Path

class StackedAreaIntegrationValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0

    def log_success(self, message):
        """记录成功信息"""
        self.success_count += 1
        print(f"✅ {message}")

    def log_error(self, message):
        """记录错误信息"""
        self.errors.append(message)
        print(f"❌ {message}")

    def log_warning(self, message):
        """记录警告信息"""
        self.warnings.append(message)
        print(f"⚠️ {message}")

    def check_file_exists(self, filepath, description):
        """检查文件是否存在"""
        self.total_checks += 1
        full_path = self.project_root / filepath
        if full_path.exists():
            self.log_success(f"{description}: {filepath}")
            return True
        else:
            self.log_error(f"{description}文件不存在: {filepath}")
            return False

    def check_file_content(self, filepath, patterns, description):
        """检查文件内容是否包含指定模式"""
        self.total_checks += 1
        full_path = self.project_root / filepath
        
        if not full_path.exists():
            self.log_error(f"文件不存在，无法检查内容: {filepath}")
            return False

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    continue
                else:
                    self.log_error(f"{description} - 未找到模式 '{pattern}' 在文件: {filepath}")
                    return False
                    
            self.log_success(f"{description}: {filepath}")
            return True
            
        except Exception as e:
            self.log_error(f"读取文件失败 {filepath}: {e}")
            return False

    def validate_vue_component(self):
        """验证Vue组件"""
        print("\n📦 验证Vue组件...")
        
        # 检查主组件文件
        component_path = "src/components/dashboard/StackedAreaChartComponent.vue"
        if not self.check_file_exists(component_path, "堆叠面积图组件"):
            return
            
        # 检查组件内容
        component_patterns = [
            r"StackedAreaChartComponent",
            r"stackedAreaData",
            r"xAxisValues",
            r"tableData",
            r"Plotly\.newPlot"
        ]
        
        self.check_file_content(
            component_path, 
            component_patterns,
            "组件关键代码"
        )

    def validate_component_integration(self):
        """验证组件集成"""
        print("\n🔧 验证组件集成...")
        
        # 检查ComponentRenderer集成
        renderer_path = "src/components/dashboard/ComponentRenderer.vue"
        if self.check_file_exists(renderer_path, "组件渲染器"):
            patterns = [
                r"StackedAreaChartComponent",
                r"stackedAreaChart",
                r"import.*StackedAreaChartComponent"
            ]
            self.check_file_content(renderer_path, patterns, "组件渲染器集成")

    def validate_routing(self):
        """验证路由配置"""
        print("\n🛣️ 验证路由配置...")
        
        # 检查路由文件
        router_path = "src/router/index.js"
        if self.check_file_exists(router_path, "路由配置"):
            patterns = [
                r"StackedAreaDemo",
                r"/stacked-area-demo"
            ]
            self.check_file_content(router_path, patterns, "路由配置")
            
        # 检查演示页面
        demo_path = "src/views/StackedAreaDemo.vue"
        if self.check_file_exists(demo_path, "演示页面"):
            patterns = [
                r"StackedAreaDemoPage",
                r"StackedAreaChartComponent"
            ]
            self.check_file_content(demo_path, patterns, "演示页面内容")

    def validate_home_integration(self):
        """验证主页集成"""
        print("\n🏠 验证主页集成...")
        
        home_path = "src/views/Home.vue"
        if self.check_file_exists(home_path, "主页"):
            patterns = [
                r"stacked-area-demo",
                r"堆叠面积图"
            ]
            self.check_file_content(home_path, patterns, "主页链接")

    def validate_backend_api(self):
        """验证后端API"""
        print("\n🌐 验证后端API...")
        
        # 检查演示服务器
        demo_api_path = "api/show_plate_server_demo.py"
        if self.check_file_exists(demo_api_path, "演示API服务器"):
            patterns = [
                r"stacked-area-demo",
                r"generate_mock_stacked_area_data",
                r"stackedAreaData"
            ]
            self.check_file_content(demo_api_path, patterns, "演示API集成")
            
        # 检查生产服务器
        prod_api_path = "api/show_plate_server_multiplate_v2.py"
        if self.check_file_exists(prod_api_path, "生产API服务器"):
            patterns = [
                r"get_sector_stacked_area_data",
                r"stacked-area-sector"
            ]
            self.check_file_content(prod_api_path, patterns, "生产API集成")

    def validate_documentation(self):
        """验证文档"""
        print("\n📚 验证文档...")
        
        # 检查使用指南
        guide_path = "docs/STACKED_AREA_CHART_GUIDE.md"
        self.check_file_exists(guide_path, "使用指南")
        
        # 检查更新摘要
        update_path = "STACKED_AREA_CHART_UPDATE.md"
        self.check_file_exists(update_path, "更新摘要")

    def validate_tools_and_scripts(self):
        """验证工具和脚本"""
        print("\n🛠️ 验证工具和脚本...")
        
        # 检查演示脚本
        script_path = "scripts/demo-stacked-area-chart.py"
        if self.check_file_exists(script_path, "演示脚本"):
            patterns = [
                r"generate_stacked_area_demo_data",
                r"stackedAreaData"
            ]
            self.check_file_content(script_path, patterns, "演示脚本功能")
        
        # 检查VS Code任务
        tasks_path = ".vscode/tasks.json"
        if self.check_file_exists(tasks_path, "VS Code任务配置"):
            patterns = [
                r"堆叠面积图演示",
                r"demo-stacked-area-chart.py"
            ]
            self.check_file_content(tasks_path, patterns, "VS Code任务配置")
            
        # 检查启动脚本
        if os.name == 'nt':  # Windows
            script_name = "test-stacked-area-chart.bat"
        else:  # Linux/Mac
            script_name = "test-stacked-area-chart.sh"
        
        self.check_file_exists(script_name, "启动脚本")

    def check_package_dependencies(self):
        """检查包依赖"""
        print("\n📦 检查包依赖...")
        
        package_json_path = "package.json"
        if self.check_file_exists(package_json_path, "package.json"):
            try:
                with open(self.project_root / package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                # 检查关键依赖
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})
                all_deps = {**dependencies, **dev_dependencies}
                
                required_deps = ['vue', 'plotly.js-dist', 'axios']
                for dep in required_deps:
                    if dep in all_deps:
                        self.log_success(f"依赖检查: {dep} - {all_deps[dep]}")
                        self.total_checks += 1
                    else:
                        self.log_warning(f"可能缺少依赖: {dep}")
                        self.total_checks += 1
                        
            except Exception as e:
                self.log_error(f"读取package.json失败: {e}")

    def run_validation(self):
        """运行完整验证"""
        print("🔍 开始验证堆叠面积图组件集成...")
        print("=" * 60)
        
        # 运行所有验证
        self.validate_vue_component()
        self.validate_component_integration()
        self.validate_routing()
        self.validate_home_integration()
        self.validate_backend_api()
        self.validate_documentation()
        self.validate_tools_and_scripts()
        self.check_package_dependencies()
        
        # 输出结果摘要
        print("\n" + "=" * 60)
        print("📊 验证结果摘要:")
        print(f"   ✅ 成功: {self.success_count}/{self.total_checks}")
        print(f"   ❌ 错误: {len(self.errors)}")
        print(f"   ⚠️ 警告: {len(self.warnings)}")
        
        success_rate = (self.success_count / self.total_checks) * 100 if self.total_checks > 0 else 0
        print(f"   📈 成功率: {success_rate:.1f}%")
        
        # 输出详细错误信息
        if self.errors:
            print("\n❌ 发现的错误:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
                
        if self.warnings:
            print("\n⚠️ 发现的警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        # 给出建议
        print("\n💡 建议:")
        if success_rate >= 90:
            print("   🎉 集成验证基本通过！可以开始测试功能")
            print("   🚀 运行 test-stacked-area-chart.bat 或 test-stacked-area-chart.sh 开始测试")
        elif success_rate >= 70:
            print("   🔧 大部分集成正常，但有一些问题需要修复")
            print("   📋 请根据上面的错误信息进行修复")
        else:
            print("   🚨 发现较多问题，建议仔细检查文件完整性")
            print("   📞 如需帮助，请查看 docs/STACKED_AREA_CHART_GUIDE.md")
            
        print("\n📚 相关文档:")
        print("   - 使用指南: docs/STACKED_AREA_CHART_GUIDE.md")
        print("   - 更新摘要: STACKED_AREA_CHART_UPDATE.md")
        print("   - 演示脚本: python scripts/demo-stacked-area-chart.py")
        
        return len(self.errors) == 0

def main():
    """主函数"""
    validator = StackedAreaIntegrationValidator()
    
    try:
        success = validator.run_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 验证过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
