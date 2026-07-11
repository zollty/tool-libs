# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import ctypes
from ctypes import wintypes
import sys
import os
import shutil
import time


def fast_delete(folder_path):
    """快速删除文件夹及其所有内容"""

    if not os.path.exists(folder_path):
        print(f"错误: 路径不存在 '{folder_path}'")
        return False

    if not os.path.isdir(folder_path):
        print(f"错误: 路径不是文件夹 '{folder_path}'")
        return False

    # 确认删除
    confirm = input(f"确定要永久删除 '{folder_path}' 及其所有内容吗? [y/N] ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return False

    print("正在删除... (这可能需要一些时间)")

    start_time = time.time()

    try:
        # 使用shutil.rmtree删除文件夹
        shutil.rmtree(folder_path)
    except Exception as e:
        print(f"删除过程中出错: {str(e)}")
        return False

    elapsed_time = time.time() - start_time

    # 验证删除结果
    if os.path.exists(folder_path):
        print("警告: 删除操作可能未完全成功")
        return False
    else:
        print(f"删除完成，耗时 {elapsed_time:.2f} 秒")
        return True


def fast_delete_win32(folder_path):
    """Windows系统下的极速删除方案"""
    try:
        # 定义必要的Windows类型和常量
        FO_DELETE = 0x0003
        FOF_NOCONFIRMATION = 0x0010
        FOF_NOERRORUI = 0x0400
        FOF_SILENT = 0x0004

        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [
                ("hwnd", wintypes.HWND),
                ("wFunc", ctypes.c_uint),
                ("pFrom", ctypes.c_wchar_p),  # 修改为c_wchar_p
                ("pTo", ctypes.c_wchar_p),  # 修改为c_wchar_p
                ("fFlags", ctypes.c_ushort),
                ("fAnyOperationsAborted", wintypes.BOOL),
                ("hNameMappings", wintypes.LPVOID),
                ("lpszProgressTitle", ctypes.c_wchar_p),
            ]

        shell32 = ctypes.WinDLL('shell32', use_last_error=True)
        SHFileOperationW = shell32.SHFileOperationW
        SHFileOperationW.argtypes = [ctypes.POINTER(SHFILEOPSTRUCTW)]
        SHFileOperationW.restype = ctypes.c_int

        # 准备路径字符串(必须以双空字符结尾)
        path = os.path.abspath(folder_path)
        path = path.replace('/', '\\')
        if not path.endswith('\0\0'):
            path += '\0\0'  # 双空字符终止

        # 创建结构体实例
        op = SHFILEOPSTRUCTW()
        op.hwnd = None
        op.wFunc = FO_DELETE
        op.pFrom = ctypes.c_wchar_p(path)  # 显式转换为c_wchar_p
        op.pTo = None
        op.fFlags = FOF_NOCONFIRMATION | FOF_NOERRORUI | FOF_SILENT
        op.fAnyOperationsAborted = False
        op.hNameMappings = None
        op.lpszProgressTitle = None

        # 执行删除操作
        result = SHFileOperationW(ctypes.byref(op))

        if result != 0:
            print(f"删除操作失败，错误代码: {result}")
            return False
        # 验证删除结果
        if os.path.exists(folder_path):
            print("警告: 删除操作可能未完全成功")
            return False
        return True
    except Exception as e:
        print(f"Windows API删除失败: {str(e)}")
        return False


def delete_dir(folder_path, with_confirm=False):
    """快速删除文件夹及其所有内容，优先调用 fast_delete_win32，如不支持再调用fast_delete """
    if not os.path.exists(folder_path):
        print(f"错误: 路径不存在 '{folder_path}'")
        sys.exit(1)

    if not os.path.isdir(folder_path):
        print(f"错误: 路径不是文件夹 '{folder_path}'")
        sys.exit(1)

    # 确认删除
    if with_confirm:
        confirm = input(f"确定要永久删除 '{folder_path}' 及其所有内容吗? [y/N] ")
        if confirm.lower() != 'y':
            print("操作已取消")
            sys.exit(0)

    print("正在删除... (这可能需要一些时间)")
    start_time = time.time()

    if sys.platform == 'win32':
        success = fast_delete_win32(folder_path)
    else:
        success = fast_delete(folder_path)

    elapsed_time = time.time() - start_time
    if success:
        print(f"删除成功完成，耗时: {elapsed_time:.1f}秒")
        sys.exit(0)
    else:
        print(f"删除失败，耗时: {elapsed_time:.1f}秒")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("错误: 必须指定要删除的文件夹路径")
        print(f"用法: {sys.argv[0]} <文件夹路径>")
        sys.exit(1)

    folder_path = sys.argv[1]
    delete_dir(folder_path, with_confirm=True)
