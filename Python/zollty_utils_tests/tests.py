import os
import re
from zollty_utils.openpy_excel_utils import load_workbook, read_sheet_with_merged_cells, write_excel_with_merged_cells
import os
import csv
from glob import glob

def load_order_map(file_path):
    # 调用函数并获取数据
    ws = load_workbook(file_path)
    data = read_sheet_with_merged_cells(ws.active)

    # 遍历打印数据（最后一列为原始行号）
    # for row_index, row_data in enumerate(data, start=1):
    #     print(f"行 {row_index}（原始行号：{row_data[-1]}）: {row_data}")

    result_data = {}
    # 遍历打印数据（最后一列为原始行号）
    for row_index, row in enumerate(data, start=1):
        # print(f"行 {row_index}（原始行号：{row[-1]}）: {row}")
        key = row[1]
        value = row[0]
        # item = map(key, value)
        # print(f"行 {row_index}（原始行号：{row[-1]}）: {key}:{value}")
        result_data[key] = value

    return result_data

def natural_sort_key(s):
    """模拟 Windows 文件管理器的自然排序"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def extract_ticket_from_filename(filename):
    """
    从文件名提取单号。格式: 编号__字母__数字__单号
    仅当数字不等于 0.00 或 -0.00 时返回单号，否则返回 None
    """
    # 去掉扩展名，按 '__' 分割
    name_without_ext = os.path.splitext(filename)[0]
    parts = name_without_ext.split('__')

    if len(parts) != 4:
        return None

    if parts[2] == '0.00' or parts[2] == '-0.00':
        return None

    # try:
    #     number = float(parts[2])
    # except ValueError:
    #     return None
    #
    # # 判断是否为 0.00 或 -0.00
    # if abs(number) < 1e-9:
    #     return None

    return parts[3]


def process_directories(directories):
    idx = 0
    for directory in directories:
        print(f"处理目录: {directory}-------------------------------------------{order_files[idx]}")
        order_map = load_order_map(order_files[idx])
        idx = idx + 1
        if not os.path.isdir(directory):
            print(f"目录不存在或不是文件夹: {directory}")
            continue

        for filename in sorted(os.listdir(directory), key=natural_sort_key):
            ticket = extract_ticket_from_filename(filename)
            if ticket:
                if ticket in order_map:
                    print(order_map[ticket])
                else:
                    print(f"未找到单号: {ticket}")
            # else:
            #     print(f"NOT: {filename}")

if __name__ == "__main__":
    # 指定要扫描的目录
    target_dirs = [
        r"D:\__SYNC2\git-dms\所有订单资金记录\data1",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data2",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data3",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data4",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data5",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data6",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data7",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data8",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data9",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data10",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data11",
        r"D:\__SYNC2\git-dms\所有订单资金记录\data12",
    ]

    order_files = [
        r"D:\__SYNC0-P\Desktop\无标题11.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题12.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题13.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题14.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题15.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题16.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题17.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题18.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题19.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题20.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题21.xlsx",
        r"D:\__SYNC0-P\Desktop\无标题22.xlsx",
    ]

    process_directories(target_dirs)
