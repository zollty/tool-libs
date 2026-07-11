from zollty_utils.openpy_excel_utils import load_workbook, read_sheet_with_merged_cells, write_excel_with_merged_cells
import os
import csv
from glob import glob

def load_order_map(file_path):
    # 调用函数并获取数据
    ws = load_workbook(file_path)
    data = read_sheet_with_merged_cells(ws.active)

    result_data = {}
    # 遍历打印数据（最后一列为原始行号）
    for row_index, row in enumerate(data, start=1):
        # print(f"行 {row_index}（原始行号：{row[-1]}）: {row}")
        key = row[1]
        value = row[0]
        # item = map(key, value)
        print(f"行 {row_index}（原始行号：{row[-1]}）: {key}:{value}")
        result_data[key] = value

    return result_data


if __name__ == "__main__":
    # 指定要扫描的目录
    target_dirs = [
        r"D:\__SYNC0-P\Desktop\无标题11.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题12.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题13.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题14.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题15.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题16.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题17.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题18.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题19.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题20.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题21.xlsx",
        # r"D:\__SYNC0-P\Desktop\无标题21.xlsx",
    ]

    for directory in target_dirs:
        order_map = load_order_map(directory)
        order = '2024CAMS10070002'
        if order in order_map:
            print(order_map[order])
