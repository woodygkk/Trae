# 静默安装参数预设库
# 常见软件的默认静默安装参数

SILENT_PARAMS_DB = {
    # ========== 运行库 ==========
    "vcredist": "/S /norestart",
    "vcredist_2015": "/S /norestart",
    "vcredist_2017": "/S /norestart",
    "vcredist_2015-2022": "/S /norestart",
    "vc++": "/S /norestart",
    "visual c++": "/S /norestart",

    # .NET Framework
    "dotnetfx": "/q /norestart",
    "dotnetfx35": "/q /norestart",
    "dotnetfx40": "/q /norestart",
    "dotnetfx45": "/q /norestart",
    ".net": "/q /norestart",
    ".net framework": "/q /norestart",

    # ========== 浏览器 ==========
    "chrome": "--silent --installed-from=web",
    "google chrome": "--silent --installed-from=web",
    "firefox": "-ms",
    "microsoft edge": "-passive",

    # ========== 办公软件 ==========
    "wps": "-sp- /norestart",
    "office": "/quiet /norestart",
    "word": "/quiet /norestart",
    "excel": "/quiet /norestart",
    "pdf": "/S /norestart",
    "acrobat": "/S /norestart",
    "sumatrapdf": "-install",

    # ========== 解压软件 ==========
    "7zip": "/S",
    "winrar": "/S",
    "bandizip": "-y",
    "peazip": "/S /norestart",

    # ========== 播放器 ==========
    "vlc": "/S",
    "potplayer": "/S",
    "kmplayer": "/S",
    "foobar2000": "/S",

    # ========== 聊天软件 ==========
    "qq": "/S /norestart",
    "微信": "/S /norestart",
    "tim": "/S /norestart",
    "钉钉": "/S",
    "飞书": "/S",

    # ========== 输入法 ==========
    "搜狗输入法": "/S",
    "百度输入法": "/S",
    "微软输入法": "/S",

    # ========== 远程工具 ==========
    "teamviewer": "/S",
    "向日葵": "/S",
    "anydesk": "/S",

    # ========== 下载工具 ==========
    "idm": "-s",
    "motrix": "/S",
    "qbittorrent": "/S",

    # ========== 开发工具 ==========
    "vscode": "/VERYSILENT /NORESTART /MERGETASKS=!runcode",
    "notepad++": "/S",
    "sublime": "/S",
    "git": "/VERYSILENT",
    "nodejs": "/silent",
    "python": "/quiet InstallAllUsers=1 PrependPath=1",
    "java": "/s",
    "jdk": "/s",

    # ========== 设计工具 ==========
    "photoshop": "--silent",
    "illustrator": "--silent",
    "figma": "--silent",
    "sketch": "/S",

    # ========== 压缩软件 ==========
    "winrar": "/S",
    "7z": "/S",
    "hamster": "/S",

    # ========== 工具类 ==========
    "everything": "/S",
    "listary": "/S",
    "ditto": "/S",
    "snipaste": "/S",
    "screen_to_gif": "/S",
    "obs": "/S",
    "postman": "-s",
    "typora": "/S",
    "marktext": "/S",

    # ========== 硬件驱动 ==========
    "nvidia": "/s",
    "amd": "/s",
    "intel": "/s",
}

# MSI 默认参数
MSI_DEFAULT_PARAMS = "/qn /norestart"

# BAT/CMD 默认参数
BAT_DEFAULT_PARAMS = ""

# 未知软件的默认参数
DEFAULT_EXE_PARAMS = "/S"
DEFAULT_MSI_PARAMS = "/qn /norestart"


def get_silent_params(software_name: str, file_ext: str) -> str:
    """
    根据软件名称和文件类型获取静默安装参数

    Args:
        software_name: 软件名称（不含扩展名）
        file_ext: 文件扩展名（.exe, .msi, .bat, .cmd）

    Returns:
        静默安装参数字符串
    """
    name_lower = software_name.lower()
    ext_lower = file_ext.lower()

    # 精确匹配
    for key, params in SILENT_PARAMS_DB.items():
        if key in name_lower:
            return params

    # 根据文件类型返回默认参数
    if ext_lower == ".msi":
        return MSI_DEFAULT_PARAMS
    elif ext_lower in [".bat", ".cmd"]:
        return BAT_DEFAULT_PARAMS
    else:
        return DEFAULT_EXE_PARAMS
