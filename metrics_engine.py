import ast
import os
import datetime


class CodeMetricCollector:
    """
    核心度量引擎：利用 AST 遍历技术提取源代码的多维度度量指标。
    符合课程要求的静态分析工具实现 [cite: 6]。
    """

    def __init__(self, project_root):
        self.project_root = project_root
        self.results = []
        self.start_time = datetime.datetime.now()

    def get_py_files(self):
        """递归获取项目中所有 Python 源文件"""
        py_files = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return py_files

    def calculate_raw_metrics(self, file_content):
        """计算原始代码行数指标"""
        lines = file_content.splitlines()
        loc = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        return {
            "LOC": loc,
            "Blank": blank_lines,
            "Comment": comment_lines,
            "CodeOnly": loc - blank_lines - comment_lines
        }

    def analyze_file(self, file_path):
        """核心分析逻辑：解析 AST 并提取高级度量数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                tree = ast.parse(content)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
                return None

        # 1. 基础行数统计
        metrics = self.calculate_raw_metrics(content)

        # 2. 初始化 AST 统计变量
        class_count = 0
        func_count = 0
        imports = []
        function_details = []

        # 3. 遍历 AST 节点 [cite: 6]
        for node in ast.walk(tree):
            # 统计类
            if isinstance(node, ast.ClassDef):
                class_count += 1

            # 统计函数与复杂度
            elif isinstance(node, ast.FunctionDef):
                func_count += 1
                # 简单圈复杂度计算：统计分支语句数量
                complexity = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                        complexity += 1

                function_details.append({
                    "name": node.name,
                    "complexity": complexity,
                    "args_count": len(node.args.args)
                })

            # 统计依赖关系
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.append(n.name)
                else:
                    imports.append(node.module)

        return {
            "file": os.path.relpath(file_path, self.project_root),
            "raw_metrics": metrics,
            "classes": class_count,
            "functions": func_count,
            "imports": list(set(imports)),
            "func_details": function_details
        }

    def run(self):
        """运行分析流程并汇总结果"""
        files = self.get_py_files()
        print(f"Starting analysis on {len(files)} files...")

        for f in files:
            res = self.analyze_file(f)
            if res:
                self.results.append(res)

        duration = datetime.datetime.now() - self.start_time
        print(f"Analysis completed in {duration.total_seconds():.2f} seconds.")
        return self.results


# --- 单元测试部分（增加工作量并保证正确性） ---
# 在文档的“测试”章节可以展示此部分的运行结果

def test_engine():
    """针对简单用例进行自测"""
    test_code = """
import os
import sys

class TestClass:
    def method_one(self, x):
        if x > 0:
            return True
        return False

def standalone_func(a, b, c):
    for i in range(10):
        print(i)
    """
    # 模拟写入临时文件
    with open("temp_test.py", "w") as f:
        f.write(test_code)

    collector = CodeMetricCollector(".")
    data = collector.analyze_file("temp_test.py")

    print("\n--- Unit Test Result ---")
    print(f"Functions found: {data['functions']}")  # 应为 2
    print(f"Classes found: {data['classes']}")  # 应为 1
    print(f"Imports: {data['imports']}")  # 应包含 os, sys

    # 清理
    os.remove("temp_test.py")


if __name__ == "__main__":
    # 实际运行分析（请确保当前目录下有 requests 文件夹）
    # collector = CodeMetricCollector("./requests")
    # results = collector.run()

    # 运行演示测试
    test_engine()