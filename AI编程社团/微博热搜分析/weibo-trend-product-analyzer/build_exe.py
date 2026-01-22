import subprocess
import sys
import os

def build_executable():
    print("开始打包程序...")
    
    # 确保已安装pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("未检测到 PyInstaller，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 打包命令
    # --noconsole: 不显示控制台窗口 (GUI程序推荐)
    # --onefile: 打包成单个exe文件
    # --name: 指定exe名称
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name=WeiboAI_Assistant",
        "gui_main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n打包完成！")
        print(f"可执行文件位于: {os.path.join(os.getcwd(), 'dist', 'WeiboAI_Assistant.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")

if __name__ == "__main__":
    build_executable()
