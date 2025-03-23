#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import re
import sys
import json

FASTBOOT_METHODS = {
    "小米/红米": "关机状态下，同时长按【音量下键】+【电源键】",
    "华为/荣耀": "关机状态下，同时长按【音量上键】+【音量下键】+【电源键】",
    "OPPO": "关机状态下，同时长按【音量下键】+【电源键】",
    "VIVO": "关机状态下，同时长按【音量上键】+【电源键】",
    "三星": "关机状态下，同时长按【音量上键】+【音量下键】+【Home键】",
    "魅族": "关机状态下，同时长按【音量下键】+【电源键】",
    "一加": "关机状态下，同时长按【音量上键】+【音量下键】+【电源键】",
    "Realme": "关机状态下，同时长按【音量下键】+【电源键】",
    "其他通用方法": "1. 关机状态下尝试音量键+电源键组合\n2. 开机状态下，打开开发者选项，点击重启到bootloader"
}

class AndroidDeviceInfoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Android设备信息识别工具")
        self.root.geometry("800x600")
        self.device_info = {}
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=0, column=0, columnspan=2, pady=10)
        
        # 检测设备按钮
        self.detect_button = ttk.Button(self.button_frame, text="检测设备", command=self.detect_device)
        self.detect_button.grid(row=0, column=0, padx=5)
        
        # Fastboot指南按钮
        self.guide_button = ttk.Button(self.button_frame, text="Fastboot模式指南", command=self.show_fastboot_guide)
        self.guide_button.grid(row=0, column=1, padx=5)
        
        # 创建信息显示区域
        self.info_text = scrolledtext.ScrolledText(self.main_frame, width=70, height=20)
        self.info_text.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0, columnspan=2)
        self.status_var.set("准备就绪")

    def execute_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return None

    def check_fastboot_mode(self):
        result = self.execute_command('fastboot devices')
        return bool(result and result.strip())

    def check_adb_mode(self):
        result = self.execute_command('adb devices')
        return bool(result and 'device' in result)

    def get_fastboot_info(self):
        self.status_var.set("正在通过 Fastboot 获取设备信息...")
        self.root.update()
        
        commands = {
            '产品名称': 'fastboot getvar product 2>&1',
            '序列号': 'fastboot getvar serialno 2>&1',
            '安全状态': 'fastboot getvar secure 2>&1',
            'Bootloader版本': 'fastboot getvar version-bootloader 2>&1'
        }
        
        for key, command in commands.items():
            result = self.execute_command(command)
            if result:
                match = re.search(rf'{key.split("：")[-1]}: (.*)', result)
                if match:
                    self.device_info[key] = match.group(1)

    def get_adb_info(self):
        self.status_var.set("正在通过 ADB 获取设备信息...")
        self.root.update()
        
        commands = {
            '设备型号': 'adb shell getprop ro.product.model',
            'Android版本': 'adb shell getprop ro.build.version.release',
            '系统版本号': 'adb shell getprop ro.build.display.id',
            'CPU架构': 'adb shell getprop ro.product.cpu.abi'
        }
        
        for key, command in commands.items():
            result = self.execute_command(command)
            if result:
                self.device_info[key] = result

    def detect_device(self):
        self.info_text.delete(1.0, tk.END)
        self.device_info.clear()
        
        self.status_var.set("正在检查设备连接状态...")
        self.root.update()
        
        if self.check_fastboot_mode():
            self.info_text.insert(tk.END, "设备处于 Fastboot 模式\n\n")
            self.get_fastboot_info()
        elif self.check_adb_mode():
            self.info_text.insert(tk.END, "设备处于 ADB 模式\n\n")
            self.get_adb_info()
        else:
            self.info_text.insert(tk.END, "未检测到设备连接！\n\n")
            self.info_text.insert(tk.END, "请确保：\n")
            self.info_text.insert(tk.END, "1. 设备已正确连接到电脑\n")
            self.info_text.insert(tk.END, "2. 已安装 ADB 和 Fastboot 工具\n")
            self.info_text.insert(tk.END, "3. 设备已启用开发者选项和 USB 调试\n")
            self.status_var.set("未检测到设备")
            return
        
        if self.device_info:
            self.info_text.insert(tk.END, "设备信息:\n")
            self.info_text.insert(tk.END, "-" * 50 + "\n")
            for key, value in self.device_info.items():
                self.info_text.insert(tk.END, f"{key}: {value}\n")
            self.info_text.insert(tk.END, "-" * 50 + "\n")
            self.status_var.set("设备信息获取完成")
        else:
            self.info_text.insert(tk.END, "未能获取到设备信息！\n")
            self.status_var.set("获取设备信息失败")

    def show_fastboot_guide(self):
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Fastboot模式进入指南")
        guide_window.geometry("500x400")
        
        guide_text = scrolledtext.ScrolledText(guide_window, width=50, height=20)
        guide_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        guide_text.insert(tk.END, "各品牌手机进入Fastboot模式的方法：\n\n")
        for brand, method in FASTBOOT_METHODS.items():
            guide_text.insert(tk.END, f"【{brand}】\n{method}\n\n")
        
        guide_text.configure(state='disabled')

def main():
    root = tk.Tk()
    app = AndroidDeviceInfoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 