import ast
import os
import datetime


class StaticLintAnalyzer(ast.NodeVisitor):
    """
    高级静态代码扫描与质量审计引擎。
    本工具通过继承 ast.NodeVisitor，实现了对抽象语法树的深度遍历与自定义规则检测。
    """

    def __init__(self):
        self.issues = []
        self.current_file = ""
        # 统计各类问题的数量，用于后续报表生成
        self.summary_stats = {
            "Maintainability": 0,
            "Security": 0,
            "Code_Smell": 0
        }

    def analyze_project(self, directory):
        """
        递归遍历项目目录，对所有 Python 文件执行静态扫描。
        """
        print(f"[{datetime.datetime.now()}] 启动项目静态扫描: {directory}")

        if not os.path.exists(directory):
            print(f"错误: 路径 {directory} 不存在。")
            return []

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    self.current_file = full_path
                    self.scan_file(full_path)

        return self.issues

    def scan_file(self, file_path):
        """解析并访问单个文件的 AST 结构"""
        self.current_file = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                tree = ast.parse(source)
                self.visit(tree)
        except Exception as e:
            print(f"跳过文件 {file_path}: 解析错误 {e}")

    # ---------------------------------------------------------
    # 规则 1: 检测空异常处理 (except: pass)
    # ---------------------------------------------------------
    def visit_ExceptHandler(self, node):
        """
        检测是否存在静默忽略异常的情况。这会导致程序在出错时没有任何日志或反馈。
        """
        # 检查 except 块中是否只有单一的 pass 语句
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self._add_issue(node, "Code_Smell", "检测到空的 except: pass 块。建议增加日志记录或异常处理逻辑。")
        self.generic_visit(node)

    # ---------------------------------------------------------
    # 规则 2: 检测过度复杂的函数参数 (Maintainability)
    # ---------------------------------------------------------
    def visit_FunctionDef(self, node):
        """
        检测函数参数个数。过多的参数会增加函数的耦合度，降低可测试性。
        """
        # 获取所有参数名
        arg_names = [arg.arg for arg in node.args.args]
        # 过滤掉 Python 类方法中常见的 self 和 cls
        clean_args = [a for a in arg_names if a not in ['self', 'cls']]

        # 设置阈值为 6
        limit = 6
        if len(clean_args) > limit:
            self._add_issue(
                node,
                "Maintainability",
                f"函数 '{node.name}' 的参数过多 ({len(clean_args)} > {limit})。建议通过对象封装参数。"
            )
        self.generic_visit(node)

    # ---------------------------------------------------------
    # 规则 3: 检测潜在的硬编码敏感信息 (Security)
    # ---------------------------------------------------------
    def visit_Constant(self, node):
        """
        静态检测源码中是否包含疑似 Token、密码或 API 密钥的字符串。
        """
        if isinstance(node.value, str):
            # 定义敏感词库
            sensitive_keywords = ['token', 'password', 'secret', 'apikey', 'auth_key', 'access_id']
            val_lower = node.value.lower()

            for key in sensitive_keywords:
                if key in val_lower and len(node.value) > 0:
                    # 长度过滤：通常极短的字符串（如 'password' 标签本身）不是泄漏，长随机串才是。
                    if 10 < len(node.value) < 100:
                        self._add_issue(node, "Security", f"检测到疑似硬编码敏感信息字段: '{key}'")
        self.generic_visit(node)

    # ---------------------------------------------------------
    # 规则 4: 检测高风险内置函数调用 (Security)
    # ---------------------------------------------------------
    def visit_Call(self, node):
        """
        扫描是否使用了 eval() 或 exec()，这些函数极易引起远程代码执行漏洞。
        """
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec']:
                self._add_issue(node, "Security", f"代码中包含高风险函数调用: {node.func.id}()。")
        self.generic_visit(node)

    def _add_issue(self, node, category, description):
        """记录发现的缺陷并更新统计数据"""
        self.summary_stats[category] += 1
        self.issues.append({
            "file": os.path.basename(self.current_file),
            "line": node.lineno,
            "type": category,
            "desc": description
        })

    def print_summary(self):
        """打印扫描报告总结，用于大作业文档的结果展示部分"""
        print("\n" + "=" * 60)
        print("          Requests 项目静态代码质量扫描报告")
        print("-" * 60)
        print(f"扫描时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"扫描范围: {self.current_file}")
        print("-" * 60)
        for cat, count in self.summary_stats.items():
            print(f"| {cat:20} : {count:3} 个问题")
        print("=" * 60)


# ---------------------------------------------------------
# 模块自测逻辑：通过构造包含缺陷的代码块来验证分析器有效性
# ---------------------------------------------------------
if __name__ == "__main__":
    # 构造测试用例字符串
    test_case_content = """
def sample_bad_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8):
    \"\"\"此函数包含参数过多缺陷\"\"\"
    try:
        # 模拟高风险调用
        eval("__import__('os').system('ls')")
    except:
        # 模拟空异常处理缺陷
        pass

    # 模拟硬编码敏感信息
    GITHUB_TOKEN = "ghp_JpX8v2k3L9mN1qR5tZ7wY0xS4aB6cE8iD"
    """

    test_filename = "lint_test_case.py"
    with open(test_filename, "w", encoding='utf-8') as f:
        f.write(test_case_content)

    print("--- 启动 StaticLintAnalyzer 模块自测环节 ---")
    tester = StaticLintAnalyzer()
    tester.scan_file(test_filename)

    # 输出详细发现
    for issue in tester.issues:
        print(f"[行号 {issue['line']}] 类别: {issue['type']:15} | 描述: {issue['desc']}")

    tester.print_summary()

    # 清理生成的临时测试文件
    if os.path.exists(test_filename):
        os.remove(test_filename)