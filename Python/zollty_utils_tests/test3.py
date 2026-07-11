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
        key = row[2]
        value = row[7]
        # item = map(key, value)
        # print(f"行 {row_index}（原始行号：{row[-1]}）: {key}:{value}")
        if not key:
            continue
        key = str(key).strip()
        if key in result_data:
            result_data[key] = value + result_data[key]
        else:
            result_data[key] = value

    return result_data


def load_order_map2(file_path):
    # 调用函数并获取数据
    ws = load_workbook(file_path)
    data = read_sheet_with_merged_cells(ws.active)
    result_data = {}
    # 遍历打印数据（最后一列为原始行号）
    for row_index, row in enumerate(data, start=1):
        key = row[0]
        key = str(key).strip()
        result_data[key] = row
       # print(f"行 {row_index}（原始行号：{row[-1]}）: {key}:{row}")

    return result_data


if __name__ == "__main__":

    order_files = [
        r"D:\__SYNC0-P\Desktop\130异常订单排查.xlsx",
        r"D:\__SYNC0-P\Desktop\jituan.xlsx",
    ]

    result_data = load_order_map(order_files[0])
    map_data = load_order_map2(order_files[1])
    for ie in map_data:
        print('----------------------', ie)
    for ie in result_data:
        if ie in map_data:
            print(map_data[ie][5]) #
        else:
            print(ie)
