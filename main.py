from email.policy import default

from playwright.async_api import async_playwright

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

import os
import json
import random
import psutil
import platform
import time
from datetime import datetime

from astrbot.core import AstrBotConfig


class StatusPrPr:
    def __init__(self):
        # 默认配置
        self.config = {
            "command": "prprstatus",
            "authority": 1,
            "botName": "AstrBot",
            "BackgroundURL": [
                os.path.join(os.path.dirname(__file__), 'htmlmaterial/白圣女.txt'),
                os.path.join(os.path.dirname(__file__), 'htmlmaterial/ba.txt')
            ],
            "HTML_setting": {
                "botNameColorful": False,
                "botNameColor": "rgba(85,70,163,0.8)",
                "botProfileblurs": 0.8,
                "logoblurs": 0.5,
                "Backgroundblurs": 15,
                "Backgroundcolor": "rgba(230, 215, 235, 0.692)",
                "dashboardTextColor1": "rgba(29,131,190,1)",
                "dashboardTextColor2": "rgba(149,40,180,1)",
                "dashboardTextColor3": "rgba(77,166,12,1)",
                "dashboardTextColor4": "rgba(56,91,119,1)",
                "systeminformationTextColor": "rgba(25,99,160,1)",
                "DashedboxThickn": 3,
                "Dashedboxcolor": "rgba(183,168,158,1)",
                "textfont1": "./font/Gugi-Regular.ttf",
                "textfont2": "./font/HachiMaruPop-Regular.ttf"
            },
            "consoleinfo": False
        }

    def rgba_to_hex(self, rgba):
        """将RGBA颜色转换为十六进制颜色"""
        rgba_array = [int(x) for x in rgba.replace("rgba(", "").replace(")", "").split(",")[:3]]
        r, g, b = rgba_array
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        return hex_color

    def get_random_background(self):
        """从配置的背景列表中随机选择一个背景"""
        background_path = random.choice(self.config["BackgroundURL"])

        # 网络URL
        if background_path.startswith('http://') or background_path.startswith('https://'):
            return background_path
        # 文本文件路径
        elif background_path.endswith('.txt'):
            with open(background_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            return random.choice(lines).replace('\\', '/')
        # 本地文件夹路径
        else:
            valid_extensions = ('.jpg', '.png', '.gif', '.bmp', '.webp')
            files = [f for f in os.listdir(background_path) if f.lower().endswith(valid_extensions)]
            if not files:
                raise  logger.error(f"没有找到有效的背景图片文件在路径: {background_path}")
            return os.path.join(background_path, random.choice(files)).replace('\\', '/')

    def get_cpu_usage(self):
        """获取CPU使用率"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            freq = f"{cpu_freq.current / 1000:.2f}"
        else:
            freq = "N/A"

        cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = "Unknown CPU"

        return {
            "cpuUsage": cpu_percent / 100,
            "cpuFreq": freq,
            "cpuInfo": cpu_info
        }

    def get_memory_info(self):
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        mem_total = memory.total / 1024 / 1024 / 1024
        mem_used = memory.used / 1024 / 1024 / 1024
        mem_usage = memory.percent / 100

        swap_total = swap.total / 1024 / 1024 / 1024
        swap_used = swap.used / 1024 / 1024 / 1024
        swap_usage = swap.percent / 100 if swap.total > 0 else 0

        return {
            "memTotal": f"{mem_total:.2f} GB",
            "memUsed": f"{mem_used:.2f}",
            "memUsage": mem_usage,
            "swapTotal": f"{swap_total:.2f} GB",
            "swapUsed": f"{swap_used:.2f}",
            "swapUsage": swap_usage
        }

    def get_disk_usage(self):
        """获取磁盘使用情况"""
        partitions = psutil.disk_partitions()
        total_size = 0
        used_size = 0

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_size += usage.total
                used_size += usage.used
            except:
                pass

        disk_total = total_size / 1024 / 1024 / 1024
        disk_used = used_size / 1024 / 1024 / 1024
        disk_usage = used_size / total_size if total_size > 0 else 0

        return {
            "diskTotal": f"{disk_total:.2f} GB",
            "diskUsed": f"{disk_used:.2f}",
            "diskUsage": disk_usage
        }

    def get_network_speed(self):
        """获取网络速度"""
        # 获取初始网络计数器
        net_io_counters_start = psutil.net_io_counters()

        # 等待一小段时间
        time.sleep(1)

        # 获取结束时的网络计数器
        net_io_counters_end = psutil.net_io_counters()

        # 计算间隔期间的字节发送和接收
        bytes_sent = net_io_counters_end.bytes_sent - net_io_counters_start.bytes_sent
        bytes_recv = net_io_counters_end.bytes_recv - net_io_counters_start.bytes_recv

        # 格式化网络速度显示
        def format_bytes(bytes_count):
            if bytes_count < 1024:
                return f"{bytes_count} B/s"
            elif bytes_count < 1024 ** 2:
                return f"{bytes_count / 1024:.1f} KB/s"
            elif bytes_count < 1024 ** 3:
                return f"{bytes_count / 1024 ** 2:.1f} MB/s"
            else:
                return f"{bytes_count / 1024 ** 3:.1f} GB/s"

        # 计算网络使用进度（用于可视化，最大值假设为100Mbps）
        max_speed = 100 * 1024 * 1024 / 8  # 100Mbps 转换为字节
        network_progress = min(1.0, (bytes_sent + bytes_recv) / max_speed)

        return {
            "text": f"↑ {format_bytes(bytes_sent)} ↓ {format_bytes(bytes_recv)}",
            "progress": network_progress,
            "sent": bytes_sent,
            "recv": bytes_recv
        }

    def duration_time(self, uptime_seconds):
        """格式化运行时间"""
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"正在运行中. . . . . .已持续运行 {days}天 {hours}小时 {minutes}分钟"

    def get_system_info(self, plugins_nums = 0):
        """获取系统信息"""
        cpu_info = self.get_cpu_usage()
        memory_info = self.get_memory_info()
        disk_info = self.get_disk_usage()

        system_info = {
            "dashboard": [
                {
                    "progress": cpu_info["cpuUsage"],
                    "title": f"{cpu_info['cpuUsage'] * 100:.0f}% - {cpu_info['cpuFreq']}Ghz",
                },
                {
                    "progress": memory_info["memUsage"],
                    "title": f"{memory_info['memUsed']} / {memory_info['memTotal']}",
                },
                {
                    "progress": memory_info["swapUsage"],
                    "title": f"{memory_info['swapUsed']} / {memory_info['swapTotal']}",
                },
                {
                    "progress": disk_info["diskUsage"],
                    "title": f"{disk_info['diskUsed']} / {disk_info['diskTotal']}",
                },
            ],
            "information": [
                {
                    "key": "CPU",
                    "value": cpu_info["cpuInfo"],
                },
                {
                    "key": "System",
                    "value": platform.platform(),
                },
                {
                    "key": "Version",
                    "value": "Python " + platform.python_version(),
                },
                {
                    "key": "Plugins",
                    "value": f"已经加载了{plugins_nums}个插件",
                },
            ],
        }
        return system_info

    def generate_html(self, platform_name="aiocqhttp", plugins_nums=0):
        """生成HTML页面"""
        system_info = self.get_system_info(plugins_nums)
        network_status = self.get_network_speed()
        uptime = time.time() - psutil.boot_time()

        try:
            background_image = self.get_random_background()
        except Exception as e:
            print(f"获取背景图片失败: {str(e)}")
            background_image = "https://i.loli.net/2021/03/19/2UZcj6qlLy5vndm.png"  # 默认背景

        dashboard_color = [
            self.rgba_to_hex(self.config["HTML_setting"]["dashboardTextColor1"]),
            self.rgba_to_hex(self.config["HTML_setting"]["dashboardTextColor2"]),
            self.rgba_to_hex(self.config["HTML_setting"]["dashboardTextColor3"]),
            self.rgba_to_hex(self.config["HTML_setting"]["dashboardTextColor4"])
        ]

        textfont1 = self.config["HTML_setting"]["textfont1"].replace("\\", "/")
        textfont2 = self.config["HTML_setting"]["textfont2"].replace("\\", "/")

        # 处理机器人名称样式
        if self.config["HTML_setting"]["botNameColorful"]:
            bot_name_title_text = """
#background-page .__title-text {
    font-family: "HachiMaruPop";
    font-size: 70px;
    line-height: 68px;
    /* 设置文字填充为透明 */
    color: transparent;
    /* 应用彩虹色渐变 */
    background: linear-gradient(to right,
                                #fcb5b5,
                                #fcd6ae,
                                #fde8a6,
                                #c3f7b1,
                                #aed6fa,
                                #c4aff5,
                                #f1afcc);
    /* 将背景裁切为文字形状 */
    -webkit-background-clip: text;
    /* 确保渐变仅填充文字 */
    background-clip: text;
    -webkit-text-stroke: 1px var(--main-color);
    margin-left: 18px; /* 在文本和图片之间添加一些间隔 */
    order: 1; /* 确保文本在图片后面显示 */
}
            """
        else:
            bot_name_title_text = f"""
#background-page .__title-text {{
    font-family: "HachiMaruPop";
    font-size: 60px;
    line-height: 68px;
    color: {self.config["HTML_setting"]["botNameColor"]};
    -webkit-text-stroke: 1px var(--main-color);
    margin-left: 18px; /* 在文本和图片之间添加一些间隔 */
    order: 1; /* 确保文本在图片后面显示 */
}}
            """

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />

<style>
.circle-progress {{
    --progress: 0;
    --color: black;
    position: relative; /* 使内部的圆可以相对定位 */
}}
.circle-progress .circle-progress-bar {{
    stroke-dasharray: 612.3, 612.3;
    stroke-dashoffset: calc(612.3 * (1 - var(--progress)));
    stroke: var(--color);
    stroke-linecap: round;
}}

.circle-progress .circle-background {{
    fill: none;
    stroke: #e4e2e163; /* 灰色作为背景 */
    stroke-width: 12; /* 笔触宽度与前景一致 */
}}

@font-face {{
    font-family: "HachiMaruPop";
    src: url("{textfont2}") format("truetype");
}}
@font-face {{
    font-family: "Gugi";
    src: url("{textfont1}") format("truetype");
}}
* {{
    margin: 0;
    padding: 0;
    border: 0;
}}
:root {{
    --main-color: #5546a3;
}}

#background-page {{
    width: 100%; /* 保持原有宽度 */
    height: 1872px; /* 保持原有高度 */
    margin: 0 auto; /* 居中对齐 */
    background-image: url('{background_image}'); /* 图片 */
    background-size: 100% auto; /* 使图片宽度与容器宽度一致，高度自动调整 */
    background-repeat: no-repeat;  /*防止图片重复 */
    background-position: top center; /* 图片置顶对齐 */
    padding: 636px 64px 65px;
    box-sizing: border-box;
    position: relative;
}}
#background-page:before {{
    content: "";
    position: absolute;
    top: 520px;
    left: 0;
    right: 0;
    bottom: 0;
    backdrop-filter: blur({self.config["HTML_setting"]["Backgroundblurs"]}px); /* 设置模糊半径 */
    background: {self.config["HTML_setting"]["Backgroundcolor"]}; /* 毛玻璃背景色 */ /*这个不错 202, 140, 221, 0.247*/
    z-index: 1;
    pointer-events: none;
    -webkit-mask-image: linear-gradient(to bottom, transparent, black 10%, black 90%, transparent);
    mask-image: linear-gradient(to bottom, transparent, black 8%, black 100%, transparent);
}}
#background-page .__title {{
    display: flex;
    flex-direction: row;
    align-items: center;/* 垂直居中对齐所有子元素 */
    position: relative; /* 确保title在遮罩之上 */
    justify-content: flex-start; /* 从行的开始位置对齐子元素 */
    z-index: 2;
}}
#background-page .__title-image {{
    margin-left: 10px;
    height: 85px; /* 保持图像大小 */
    order: 0; /* 设置更小的order值，让图片在文字前面显示 */
    opacity: {self.config["HTML_setting"]["botProfileblurs"]}; /* 调整透明度 */
    border-radius: 50%; /* 将图片的边框半径设置为50%，使其呈现圆形 */
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3); /* 添加一圈阴影，参数分别为水平偏移、垂直偏移、模糊半径和颜色 */
    margin-right: 20px; /* 在图片和文本之间添加一些间隔 */
}}

#background-page .__footer-image {{
    border-radius: 50%; /* 将图片的边框半径设置为50%，使其呈现圆形 */
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3); /* 添加一圈阴影，参数分别为水平偏移、垂直偏移、模糊半径和颜色 */
    margin-left: 20px; /* 调整左侧间距 */
    margin-top: -38px; /* 保持原有的垂直间距 */
    height: 85px;
    opacity: {self.config["HTML_setting"]["logoblurs"]}; /* 设置透明度 */
    z-index: 2;
    align-items: center; /* 垂直居中对齐 */
}}

#background-page .__dashboard, #background-page .__information, #background-page .__footer, #background-page .__footer-image {{
    position: relative; /* 确保这些元素在遮罩之上 */
    z-index: 2;
}}

{bot_name_title_text}

#background-page .__dashboard {{
    margin-top: 30px;
    list-style: none;
    display: flex;
    flex-direction: row; /* 水平排列 */
    flex-wrap: wrap; /* 允许项目自动换行 */
    gap: 0px;
}}

#background-page .__dashboard-block {{
    --block-color: block;
    display: flex;
    flex-direction: column; /* 保持垂直排列 */
    align-items: center; /* 在水平方向上居中对齐 */
    text-align: center; /* 文本水平居中对齐 */
    width: calc(50% - 25px); /* 计算宽度为容器宽度的一半减去间隙的一部分，假设间隙是50px */
    gap: 20px;
}}

#background-page .__dashboard-block__info {{
    margin-left: 0px;
    flex: 1;
}}

#background-page .__dashboard-block__info__value {{
    margin-top: 10px;
    font-size: 35px; /*圆圈旁边的字的大小*/
    font-family: "Gugi";
    line-height: 56px;
    color: var(--block-color);
}}
#background-page .__information {{
    margin-top: 55px;
    padding: 0 30px;
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 14px;
}}
#background-page .__information-block {{
    display: flex;
    flex-direction: row;
}}
#background-page .__information-block__key {{
    width: 185px;
}}

#background-page .__information-block__value {{
    flex: 1;
}}

#background-page .__information {{
    border: {self.config["HTML_setting"]["DashedboxThickn"]}px dashed {self.rgba_to_hex(self.config["HTML_setting"]["Dashedboxcolor"])}; /* 设置边框为深色(#333)的虚线，宽度为2px */
    padding: 30px; /* 添加内边距，使文本不紧贴边框 */
    margin-bottom: 14px; /* 保持元素之间的间隔 */
    border-radius: 10px; /* 添加圆角效果 */
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 10px;
}}
/*  __dashboard 类样式 */
#background-page .__dashboard {{
    border: {self.config["HTML_setting"]["DashedboxThickn"]}px dashed {self.rgba_to_hex(self.config["HTML_setting"]["Dashedboxcolor"])}; /* 设置边框为虚线 */
    padding: 45px; /* 添加内边距，使文本不紧贴边框 */
    margin-bottom: 14px; /* 保持元素之间的间隔 */
    border-radius: 10px; /* 添加圆角效果 */
    list-style: none;
    display: flex;
    flex-direction: row; /* 保持原有的行排列 */
    flex-wrap: wrap; /* 允许项目自动换行 */
    gap: 35px; /* 保持原有的间隙设置 */
}}
#background-page .__information-block__key,
#background-page .__information-block__key, #background-page .__information-block__value {{
    line-height: 42px;
    font-size: 32px;
    font-family: "Gugi";
    color: {self.rgba_to_hex(self.config["HTML_setting"]["systeminformationTextColor"])}; /*系统信息的颜色*/
}}

#background-page .__footer {{
    margin-top: 50px;
    font-family: "HachiMaruPop";
    font-size: 32px;
    text-align: right;
    color: #b7a89e;/*已持续运行*/
    -webkit-text-stroke: 0.5px #ff000091;  /*已持续运行*/
}}

</style>
<title>status</title>
</head>
<body>
<div id="app">
    <div id="background-page">
        <div class="__title">
            <span class="__title-text" id="config_name">{self.config["botName"]}</span>
            <!-- Insert HTML for profile image would go here -->
        </div>
        <ul class="__dashboard" id="config_dashboard">
            <!--  -->

            <!-- 第一个圆 -->
            <li
                class="__dashboard-block __cpu"
                style="--block-color: {dashboard_color[0]}"
            >
            <!-- 圆的大小 -->
            <svg
                width="112"
                height="112"
                viewBox="0 0 200 200"
                class="__dashboard-block__progress circle-progress"
                style="--progress: {system_info['dashboard'][0]['progress']}; --color: var(--block-color)"
            >
                <!-- 背景圆 -->
                <circle class="circle-shadow" cx="100" cy="100" r="98" fill="none" stroke="rgba(0, 0, 0, 0.15)" stroke-width="3"/>
                <circle
                class="circle-background"
                cx="100"
                cy="100"
                r="94"
                />
                <!-- 进度条 -->
                <circle
                class="circle-progress-bar"
                stroke-linecap="round"
                cx="100"
                cy="100"
                r="94"
                fill="none"
                transform="rotate(-93.8 100 100)"
                stroke-width="12"
                />
                <!-- 中心文字 -->
                <text
                x="50%"
                y="52%"
                font-family="Gugi"
                font-size="52"
                text-anchor="middle"
                fill="#647394"
                dy=".3em"
                >
                CPU
                </text>
            </svg>
            <div class="__dashboard-block__info">
                <p class="__dashboard-block__info__value">{system_info['dashboard'][0]['title']}</p>
            </div>
            </li>

            <!-- 第二个圆 -->
            <li
                class="__dashboard-block __cpu"
                style="--block-color: {dashboard_color[1]}"
            >
            <!-- 圆的大小 -->
            <svg
                width="112"
                height="112"
                viewBox="0 0 200 200"
                class="__dashboard-block__progress circle-progress"
                style="--progress: {system_info['dashboard'][1]['progress']}; --color: var(--block-color)"
            >
                <!-- 背景圆 -->
                <circle class="circle-shadow" cx="100" cy="100" r="98" fill="none" stroke="rgba(0, 0, 0, 0.15)" stroke-width="3"/>
                <circle
                class="circle-background"
                cx="100"
                cy="100"
                r="94"
                />
                <!-- 进度条 -->
                <circle
                class="circle-progress-bar"
                stroke-linecap="round"
                cx="100"
                cy="100"
                r="94"
                fill="none"
                transform="rotate(-93.8 100 100)"
                stroke-width="12"
                />
                <!-- 中心文字 -->
                <text
                x="50%"
                y="52%"
                font-family="Gugi"
                font-size="52"
                text-anchor="middle"
                fill="#647394"
                dy=".3em"
                >
                RAM
                </text>
            </svg>
            <div class="__dashboard-block__info">
                <p class="__dashboard-block__info__value">{system_info['dashboard'][1]['title']}</p>
            </div>
            </li>

            <!-- 第三个圆 -->
            <li
                class="__dashboard-block __cpu"
                style="--block-color: {dashboard_color[2]}"
            >

            <svg
                width="112"
                height="112"
                viewBox="0 0 200 200"
                class="__dashboard-block__progress circle-progress"
                style="--progress: {system_info['dashboard'][2]['progress']}; --color: var(--block-color)"
            >
                <!-- 背景圆 -->
                <circle class="circle-shadow" cx="100" cy="100" r="98" fill="none" stroke="rgba(0, 0, 0, 0.15)" stroke-width="3"/>
                <circle
                class="circle-background"
                cx="100"
                cy="100"
                r="94"
                />
                <!-- 进度条 -->
                <circle
                class="circle-progress-bar"
                stroke-linecap="round"
                cx="100"
                cy="100"
                r="94"
                fill="none"
                transform="rotate(-93.8 100 100)"
                stroke-width="12"
                />
                <!-- 中心文字 -->
                <text
                x="50%"
                y="52%"
                font-family="Gugi"
                font-size="52"
                text-anchor="middle"
                fill="#647394"
                dy=".3em"
                >
                SWAP
                </text>
            </svg>
            <div class="__dashboard-block__info">
                <p class="__dashboard-block__info__value">{system_info['dashboard'][2]['title']}</p>
            </div>
            </li>

            <!-- 第四个圆 -->
            <li
                class="__dashboard-block __cpu"
                style="--block-color: {dashboard_color[3]}"
            >
            <!-- 圆的大小 -->
            <svg
                width="112"
                height="112"
                viewBox="0 0 200 200"
                class="__dashboard-block__progress circle-progress"
                style="--progress: {system_info['dashboard'][3]['progress']}; --color: var(--block-color)"
            >
                <!-- 背景圆 -->
                <circle class="circle-shadow" cx="100" cy="100" r="98" fill="none" stroke="rgba(0, 0, 0, 0.15)" stroke-width="3"/>
                <circle
                class="circle-background"
                cx="100"
                cy="100"
                r="94"
                />
                <!-- 进度条 -->
                <circle
                class="circle-progress-bar"
                stroke-linecap="round"
                cx="100"
                cy="100"
                r="94"
                fill="none"
                transform="rotate(-93.8 100 100)"
                stroke-width="12"
                />
                <!-- 中心文字 -->
                <text
                x="50%"
                y="52%"
                font-family="Gugi"
                font-size="52"
                text-anchor="middle"
                fill="#647394"
                dy=".3em"
                >
                DISK
                </text>
            </svg>
            <div class="__dashboard-block__info">
                <p class="__dashboard-block__info__value">{system_info['dashboard'][3]['title']}</p>
            </div>
            </li>
            <!--  -->
        </ul>
        <ul class="__information" id="config_information">
            <!--  -->
            <!-- 系统信息 -->

            <li class="__information-block">
                <span class="__information-block__key">{system_info['information'][0]['key']}</span>
                <span class="__information-block__value">{system_info['information'][0]['value']}</span>
            </li>

            <li class="__information-block">
                <span class="__information-block__key">{system_info['information'][1]['key']}</span>
                <span class="__information-block__value">{system_info['information'][1]['value']}</span>
            </li>

            <li class="__information-block">
                <span class="__information-block__key">{system_info['information'][2]['key']}</span>
                <span class="__information-block__value">{system_info['information'][2]['value']}</span>
            </li>

            <li class="__information-block">
                <span class="__information-block__key">Platform</span>
                <span class="__information-block__value">{platform_name}</span>
            </li>

            <li class="__information-block">
                <span class="__information-block__key">Network</span>
                <span class="__information-block__value">{network_status['text']}</span>
            </li>

            <li class="__information-block">
                <span class="__information-block__key">{system_info['information'][3]['key']}</span>
                <span class="__information-block__value">{system_info['information'][3]['value']}</span>
            </li>

            </ul>
        <p class="__footer" id="config_footer">{self.duration_time(uptime)}</p>
        <img class="__footer-image" src="https://avatars.githubusercontent.com/u/197911947?s=96&v=4" />
    </div>
</div>
</body>
</html>
        """

        return html


async def render_html_to_image(content, output_path="output.png"):
    """将HTML内容渲染为图片"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 加载HTML内容
        await page.set_content(content)

        # 截图并保存
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()
    return output_path


@register("status-pro", "StatusPro", "一个显示系统状态的插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)

        is_use_default = config.get("is_use_default", True)
        background_images = config.get("background_images", [])

        background_urls = []
        # 使用默认
        if is_use_default:
            default_backgrounds = [
                os.path.join(os.path.dirname(__file__), 'htmlmaterial/白圣女.txt'),
                os.path.join(os.path.dirname(__file__), 'htmlmaterial/ba.txt')
            ]
            background_urls.extend(default_backgrounds)

        # 添加自定义
        if background_images:
            for image in background_images:
                background_urls.append(image)
        # 更新配置
        self.status_generator = StatusPrPr()
        self.status_generator.config["BackgroundURL"] = background_urls

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        logger.info("StatusPro插件已初始化")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        logger.info("StatusPro插件已卸载")


    @filter.command("status", alias={'状态', '状态查询'})
    async def handle_status_request(self, event: AstrMessageEvent) -> MessageEventResult:
        """处理请求系统状态的命令"""
        logger.info("收到系统状态请求")
        try:
            # 获取消息平台名称
            platform_name = event.platform_meta.name
            # 生成 HTML
            html_content = self.status_generator.generate_html(platform_name , plugins_nums=len(self.context.get_all_stars()))
            # 渲染 HTML 为图片
            await render_html_to_image(html_content)

            yield event.image_result("output.png")
        except Exception as e:
            logger.error(f"生成状态图片失败: {str(e)}")
            yield event.make_result().message("生成状态图片失败，请检查配置或环境。")

