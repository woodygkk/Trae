import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
from datetime import datetime
import webbrowser

# 导入分析模块
# 确保当前目录在sys.path中
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
try:
    import analyzer
except ImportError:
    # 如果直接运行此文件，analyzer可能在同一目录下
    try:
        import analyzer
    except:
        messagebox.showerror("错误", "找不到 analyzer.py 模块，请确保文件完整")
        sys.exit(1)

class WeiboAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("微博热搜AI产品分析助手")
        self.root.geometry("900x700")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("Header.TLabel", font=("微软雅黑", 12, "bold"))
        
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部控制栏
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="热搜数量:", style="TLabel").pack(side=tk.LEFT, padx=5)
        self.top_n_var = tk.StringVar(value="10")
        self.top_n_combo = ttk.Combobox(control_frame, textvariable=self.top_n_var, width=5, state="readonly")
        self.top_n_combo['values'] = ('5', '10', '20', '30')
        self.top_n_combo.pack(side=tk.LEFT, padx=5)
        
        self.analyze_btn = ttk.Button(control_frame, text="开始分析", command=self.start_analysis_thread)
        self.analyze_btn.pack(side=tk.LEFT, padx=15)
        
        self.open_report_btn = ttk.Button(control_frame, text="打开最新报告", command=self.open_latest_report, state=tk.DISABLED)
        self.open_report_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="关于", command=self.show_about).pack(side=tk.RIGHT)
        
        # 主内容区
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧日志区
        log_frame = ttk.LabelFrame(paned_window, text="运行日志", padding="5")
        paned_window.add(log_frame, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 右侧预览区 (简单显示结果摘要)
        result_frame = ttk.LabelFrame(paned_window, text="分析摘要", padding="5")
        paned_window.add(result_frame, weight=2)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, state='disabled', font=("微软雅黑", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def show_result(self, message):
        self.result_text.config(state='normal')
        self.result_text.insert(tk.END, f"{message}\n")
        self.result_text.see(tk.END)
        self.result_text.config(state='disabled')

    def start_analysis_thread(self):
        self.analyze_btn.config(state=tk.DISABLED)
        self.status_var.set("正在分析中...")
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state='disabled')
        
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()

    def run_analysis(self):
        try:
            top_n = int(self.top_n_var.get())
            self.log(f"开始获取前 {top_n} 条热搜...")
            
            # 1. 获取热搜
            hot_list = analyzer.fetch_weibo_hot(analyzer.API_URL, top_n)
            if not hot_list:
                self.log("错误: 未能获取到热搜数据")
                self.status_var.set("获取失败")
                self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
                return

            self.log(f"成功获取 {len(hot_list)} 条热搜，开始分析...")
            
            # 2. 分析每条热搜
            results = []
            for i, item in enumerate(hot_list, 1):
                title = item.get("word", "无标题")
                self.log(f"正在分析 ({i}/{len(hot_list)}): {title}")
                self.show_result(f"====== {i}. {title} ======")
                
                # 背景搜索 (模拟)
                bg_info = analyzer.search_topic_background(title)
                
                # 创意生成 (模拟，复用analyzer中的逻辑)
                # 注意：analyzer.py中 analyze_product_idea 是分析函数
                
                ideas = analyzer.analyze_product_idea({'word': title, 'hotword': title}, bg_info)
                item['background'] = bg_info
                item['ideas'] = ideas
                results.append(item)
                
                # 在界面显示简要创意
                if ideas:
                    self.show_result(f"核心痛点: {ideas.get('核心痛点', 'N/A')}")
                    self.show_result(f"产品创意: {ideas.get('产品创意', 'N/A')}")
                    self.show_result("-" * 30)
                
                # 避免请求过快
                time.sleep(1)

            # 3. 生成报告
            self.log("正在生成HTML报告...")
            report_file = analyzer.OUTPUT_PATH
            analyzer.generate_html_report(results, report_file)
            
            self.log(f"报告已生成: {report_file}")
            self.status_var.set("分析完成")
            self.last_report = report_file
            
            self.root.after(0, self.analysis_completed)

        except Exception as e:
            self.log(f"发生错误: {str(e)}")
            self.status_var.set("发生错误")
            self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
            import traceback
            traceback.print_exc()

    def analysis_completed(self):
        self.analyze_btn.config(state=tk.NORMAL)
        self.open_report_btn.config(state=tk.NORMAL)
        messagebox.showinfo("完成", f"分析完成！\n报告已保存为: {self.last_report}")

    def open_latest_report(self):
        if hasattr(self, 'last_report') and os.path.exists(self.last_report):
            webbrowser.open(os.path.abspath(self.last_report))
        else:
            # 尝试查找当天报告
            today_report = analyzer.OUTPUT_PATH
            if os.path.exists(today_report):
                webbrowser.open(os.path.abspath(today_report))
            else:
                messagebox.showinfo("提示", "找不到最新报告文件")

    def show_about(self):
        messagebox.showinfo("关于", "微博热搜AI产品分析助手 v1.0\n\n基于Trae AI编程开发\n集成了微博热搜API和AI分析模型")

if __name__ == "__main__":
    # 简单的兼容性处理
    import time
    
    root = tk.Tk()
    app = WeiboAIApp(root)
    root.mainloop()
