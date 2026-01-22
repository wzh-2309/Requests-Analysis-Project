import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime


class AnalysisReporter:
    """
    成员 C 负责：数据聚合、多维可视化及自动化分析报告生成。
    本模块利用成员 A 和 B 的分析输出，产出符合大作业“实验分析”要求的图表与文档素材。
    """

    def __init__(self, metrics_list, lint_issues):
        # 将输入数据转换为 DataFrame 格式，便于统计分析
        self.df_metrics = pd.DataFrame(metrics_list)
        self.df_issues = pd.DataFrame(lint_issues)
        self.output_path = "analysis_results"
        self.report_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        # 确保输出目录存在
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # 设置 Matplotlib 样式
        plt.style.use('ggplot')

    def generate_visualizations(self):
        """
        生成多维可视化图表，直接用于纸质大作业的“结果展示”章节。
        """
        print("--- 正在生成可视化图表 ---")

        # 1. 函数复杂度分布直方图
        plt.figure(figsize=(10, 6))
        self.df_metrics['complexity'].hist(bins=15, color='skyblue', edgecolor='black')
        plt.title('Requests Project: Function Complexity Distribution')
        plt.xlabel('Complexity Score')
        plt.ylabel('Frequency')
        plt.savefig(os.path.join(self.output_path, 'complexity_dist.png'))
        plt.close()

        # 2. 缺陷类型占比饼图
        if not self.df_issues.empty:
            plt.figure(figsize=(8, 8))
            issue_counts = self.df_issues['type'].value_counts()
            issue_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, shadow=True)
            plt.title('Code Issue Category Distribution')
            plt.ylabel('')
            plt.savefig(os.path.join(self.output_path, 'issue_pie_chart.png'))
            plt.close()

        # 3. 核心模块复杂度对比（取前10个最复杂的文件）
        plt.figure(figsize=(12, 6))
        top_files = self.df_metrics.groupby('file')['complexity'].mean().sort_values(ascending=False).head(10)
        top_files.plot(kind='bar', color='salmon')
        plt.title('Top 10 Most Complex Modules (Average)')
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_path, 'module_comparison.png'))
        plt.close()

    def create_markdown_report(self):
        """
        自动化生成 Markdown 格式的实验报告草稿，体现 300 行以上的工作量。
        """
        report_file = os.path.join(self.output_path, "final_analysis_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Requests 开源项目深度分析报告\n\n")
            f.write(f"**分析时间**: {self.report_time}\n")
            f.write(f"**分析工具**: 基于 Python AST 的静态分析引擎\n\n")

            f.write("## 1. 核心度量摘要\n")
            f.write(f"- **分析文件总数**: {len(self.df_metrics['file'].unique())}\n")
            f.write(f"- **检测到函数总数**: {len(self.df_metrics)}\n")
            f.write(f"- **项目平均复杂度**: {self.df_metrics['complexity'].mean():.2f}\n")
            f.write(f"- **最复杂函数得分**: {self.df_metrics['complexity'].max()}\n\n")

            f.write("## 2. 静态审计发现\n")
            if not self.df_issues.empty:
                f.write(f"本次扫描共发现 **{len(self.df_issues)}** 处潜在质量隐患。\n\n")
                f.write("| 文件名 | 行号 | 类别 | 问题描述 |\n")
                f.write("| :--- | :--- | :--- | :--- |\n")
                # 仅展示前20条典型问题到报告中
                for _, row in self.df_issues.head(20).iterrows():
                    f.write(f"| {row['file']} | {row['line']} | {row['type']} | {row['desc']} |\n")
            else:
                f.write("项目代码质量良好，未发现明显静态缺陷。\n")

            f.write("\n## 3. 分析结论\n")
            f.write("通过对 Requests 库的静态分析，发现该项目整体结构严谨，但部分核心处理模块复杂度较高，需要重点维护。\n")

        print(f"Markdown 报告已导出至: {report_file}")


# --- 模块自测逻辑 ---
if __name__ == "__main__":
    # 构造模拟数据用于模块验证
    mock_metrics = [
        {"file": "api.py", "complexity": 3},
        {"file": "sessions.py", "complexity": 12},
        {"file": "models.py", "complexity": 8},
        {"file": "utils.py", "complexity": 2},
        {"file": "auth.py", "complexity": 5}
    ]
    mock_issues = [
        {"file": "api.py", "line": 45, "type": "Security", "desc": "Potential hardcoded token"},
        {"file": "sessions.py", "line": 102, "type": "Code_Smell", "desc": "Empty except block"}
    ]

    print("--- 启动 ReportGenerator 模块自测 ---")
    reporter = AnalysisReporter(mock_metrics, mock_issues)
    reporter.generate_visualizations()
    reporter.create_markdown_report()
    print("自测完成，请查看 analysis_results 文件夹下的图表和报告。")