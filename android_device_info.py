#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import sys
import time

class AndroidDeviceInfo:
    def __init__(self):
        self.device_info = {}
        
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
        print("正在通过 Fastboot 获取设备信息...")
        
        # 获取产品名称
        product = self.execute_command('fastboot getvar product 2>&1')
        if product:
            self.device_info['产品名称'] = re.search(r'product: (.*)', product).group(1)

        # 获取序列号
        serialno = self.execute_command('fastboot getvar serialno 2>&1')
        if serialno:
            self.device_info['序列号'] = re.search(r'serialno: (.*)', serialno).group(1)

        # 获取安全状态
        secure = self.execute_command('fastboot getvar secure 2>&1')
        if secure:
            self.device_info['安全状态'] = re.search(r'secure: (.*)', secure).group(1)

        # 获取引导加载程序版本
        bootloader = self.execute_command('fastboot getvar version-bootloader 2>&1')
        if bootloader:
            self.device_info['Bootloader版本'] = re.search(r'version-bootloader: (.*)', bootloader).group(1)

    def get_adb_info(self):
        print("正在通过 ADB 获取设备信息...")
        
        # 获取设备型号
        model = self.execute_command('adb shell getprop ro.product.model')
        if model:
            self.device_info['设备型号'] = model

        # 获取Android版本
        android_ver = self.execute_command('adb shell getprop ro.build.version.release')
        if android_ver:
            self.device_info['Android版本'] = android_ver

        # 获取系统版本号
        build_number = self.execute_command('adb shell getprop ro.build.display.id')
        if build_number:
            self.device_info['系统版本号'] = build_number

        # 获取CPU架构
        cpu_abi = self.execute_command('adb shell getprop ro.product.cpu.abi')
        if cpu_abi:
            self.device_info['CPU架构'] = cpu_abi

    def print_info(self):
        if not self.device_info:
            print("未能获取到设备信息！")
            return
            
        print("\n设备信息:")
        print("-" * 50)
        for key, value in self.device_info.items():
            print(f"{key}: {value}")
        print("-" * 50)

def main():
    device_info = AndroidDeviceInfo()
    
    print("正在检查设备连接状态...")
    
    if device_info.check_fastboot_mode():
        print("设备处于 Fastboot 模式")
        device_info.get_fastboot_info()
    elif device_info.check_adb_mode():
        print("设备处于 ADB 模式")
        device_info.get_adb_info()
    else:
        print("未检测到设备连接！")
        print("请确保：")
        print("1. 设备已正确连接到电脑")
        print("2. 已安装 ADB 和 Fastboot 工具")
        print("3. 设备已启用开发者选项和 USB 调试")
        sys.exit(1)

    device_info.print_info()

if __name__ == "__main__":
    main() 