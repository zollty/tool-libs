import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
import zollty_utils as ut
import traceback

def __test1__(file_path):
    # 加载工作簿
    wb = openpyxl.load_workbook(file_path)
    # 获取所有sheet名称
    sheet_names = wb.sheetnames

    # 遍历所有sheet
    for sheet_name in sheet_names:
        ws = wb[sheet_name]
        # print(f"\n\n\n处理sheet：{sheet_name}--------------------------------------")
        # 处理每个sheet...
        __test1_1__(ws, sheet_name)


def __test1_1__(ws, sheet_name, debug=False):
    # 全量列名定义，最后一列为原始行号
    columns = ['[海外营销服系统业务目录]', '[海外营销服系统业务目录]', '[海外营销服系统业务目录]', '一级业务流程', '最小化业务场景名称（50字）', '最小化业务场景描述（300字）', '备注/重要说明', '使用频率', '1']

    # 定义字段索引变量
    col_idx = columns.index('1')
    business_idx = columns.index('一级业务流程')
    title_idx = columns.index('最小化业务场景名称（50字）')
    desc_idx = columns.index('最小化业务场景描述（300字）')
    remark_idx = columns.index('备注/重要说明')
    freq_idx = columns.index('使用频率')

    template = """## 序号：{idx}
### 场景目录：{dir}
### 一级业务流程：{business_idx}
### 用户场景名称：{title_idx}
### 用户场景描述：
{desc_idx}"""

    final_data = []
    try:

        data = ut.excel.read_sheet_with_merged_cells(ws)

        if debug:
            # 遍历打印数据（最后一列为原始行号）
            for row_index, row_data in enumerate(data, start=1):
                print(f"行 {row_index}（原始行号：{row_data[-1]}）: {row_data}")

        # 确保列数与每行数据长度一致
        if len(data[0]) != len(columns):
            print("警告：列数量与指定列名不匹配，请确认数据结构")
            exit()

        # 1、删除第一行表头：跳过列表中的第一个元素（即表头）。
        data = data[1:]

        # 过滤
        filtered_data = []
        for row in data:
            # if row[freq_idx] == '确定常用' or row[freq_idx] == '可能常用':
            filtered_data.append(row)

        # 处理
        final_data = []
        print(f"\n\n\n处理sheet：{sheet_name}--------------------------------------{len(filtered_data)}")
        print_str = ""
        for row in filtered_data:
            # dir = row[2] if row[2] not in (None, '') else None
            # if not dir:
            #     dir = row[1] if row[1] not in (None, '') else None
            # if not dir:
            #     dir = row[0] if row[0] not in (None, '') else None
            dir = " // ".join([s for s in row[:3] if s])
            data = {
                "idx": row[col_idx],
                "dir": "【" + sheet_name + "】 " + dir,
                "business_idx": row[business_idx],
                "title_idx": row[title_idx],
                "desc_idx": row[desc_idx]
            }
            result = template.format(**data)
            final_data.append(result)
            # tmp_print_str = print_str
            # print_str += result
            # if len(print_str) > 7000:
            #     print(tmp_print_str)
            #     print_str = result
            #     print("---------------------------------------------\n\n\n")
            # else:
            #     print(f"skip {row[col_idx]} -- {len(print_str)}")
            print(result)
            print("\n")

        # 后续处理代码...
        # print(print_str)
        print("end！")

    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'，请检查路径是否正确")
        exit(1)
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        traceback.print_exc()  # 打印完整堆栈信息
        exit(1)


# 使用示例
if __name__ == "__main__":
    file_path = input("请输入Excel文件路径: ")
    if not file_path:
        file_path = "../local/data2.xlsx"
    # 调用函数并获取数据
    __test1__(file_path)