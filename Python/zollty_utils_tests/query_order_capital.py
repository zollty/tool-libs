"""按单号查询销售订单资金情况，输出 Excel。

使用方法：
    python query_order_capital.py <单号文件路径> [输出Excel路径]

示例：
    python query_order_capital.py "D:\\work\\海外营销\\备件BO资金问题20260511\\异常单号.txt" result.xlsx
"""

import os
import sys

import pymysql
import pandas as pd

# ============================================================
# 数据库连接配置（请修改为实际信息）
# ============================================================
DB_CONFIG = {
    "host": "101.44.186.253",
    "port": 23305,
    "user": "root",
    "password": "FLP+w3My8jAVYnau",
    "database": "dms_retail",
    "charset": "utf8mb4",
}

# 查询 SQL（MySQL 参数占位符用 %(orderNo)s）
SQL = """
WITH
related_docs AS (
    SELECT so.order_no AS doc_no FROM dms_parts.t_parts_sales_order so
    WHERE so.order_no = %(orderNo)s AND so.del_flag = 0
    UNION
    SELECT bo.bo_code FROM dms_parts.t_parts_sales_order_bo bo
    WHERE bo.order_no = %(orderNo)s AND bo.del_flag = 0
    UNION
    SELECT boc.bo_cancel_code FROM dms_parts.sales_order_bo_cancel boc
    WHERE boc.order_no = %(orderNo)s AND boc.del_flag = 0
    UNION
    SELECT sp.shipment_plan_no FROM dms_parts.t_parts_shipment_plan sp
    WHERE sp.sale_order_no = %(orderNo)s AND sp.del_flag = 0
    UNION
    SELECT dd.dispatch_no FROM dms_parts.t_parts_dlr_dispatch_dtl ddd
    JOIN dms_parts.t_parts_dlr_dispatch dd ON dd.id = ddd.dispatch_id AND dd.del_flag = 0
    JOIN dms_parts.t_parts_shipment_plan sp ON sp.shipment_plan_no = ddd.shipment_plan_no AND sp.del_flag = 0
    WHERE sp.sale_order_no = %(orderNo)s AND ddd.del_flag = 0
    UNION
    SELECT md.mark_dispatch_no FROM dms_parts.t_parts_dlr_mark_dispatch md
    JOIN dms_parts.t_parts_dlr_dispatch dd ON dd.mark_dispatch_no = md.mark_dispatch_no AND dd.del_flag = 0
    JOIN dms_parts.t_parts_dlr_dispatch_dtl ddd ON ddd.dispatch_id = dd.id AND ddd.del_flag = 0
    JOIN dms_parts.t_parts_shipment_plan sp ON sp.shipment_plan_no = ddd.shipment_plan_no AND sp.del_flag = 0
    WHERE sp.sale_order_no = %(orderNo)s AND md.del_flag = 0
    UNION
    SELECT po.purchase_order FROM dms_parts.t_parts_purchase_order po
    JOIN dms_parts.t_parts_sales_order so ON so.id = po.sale_order_id AND so.del_flag = 0
    WHERE so.order_no = %(orderNo)s AND po.del_flag = 0
),
capital_flow_summary AS (
    SELECT
        SUM(CASE WHEN operate_type = 50111001 THEN amount ELSE 0 END) AS frozen_amount,
        SUM(CASE WHEN operate_type = 50111002 THEN amount ELSE 0 END) AS released_amount,
        SUM(CASE WHEN operate_type = 50111005 THEN amount ELSE 0 END) AS used_amount
    FROM tt_capital_flow
    WHERE capital_type = 50091002
      AND operate_type IN (50111001, 50111002, 50111005)
      AND (order_no LIKE CONCAT('%%', %(orderNo)s, '%%')
           OR order_no IN (SELECT doc_no FROM related_docs))
),
bo_cancel AS (
    SELECT
        order_detail_id,
        part_no,
        SUM(IFNULL(bo_cancel_quantity, 0)) AS total_cancel
    FROM dms_parts.t_parts_sales_order_bo_detail
    WHERE order_no = %(orderNo)s
        AND del_flag = 0
    GROUP BY order_detail_id, part_no
),
dispatched AS (
    SELECT
        ddd.part_no,
        SUM(ddd.bundling_qty) AS total_qty
    FROM dms_parts.t_parts_dlr_dispatch_dtl ddd
    JOIN dms_parts.t_parts_dlr_dispatch dd
        ON dd.id = ddd.dispatch_id
        AND dd.del_flag = 0
        AND dd.dispatch_status IN (80111002, 80111004)
    WHERE ddd.purchase_order_no = %(orderNo)s
        AND ddd.del_flag = 0
    GROUP BY ddd.part_no
),
pending_amount_summary AS (
    SELECT
        SUM(
            (sod.purchased_quantity
             - COALESCE(d.total_qty, 0)
             - COALESCE(bc.total_cancel, 0))
            * sod.mod_price_rate
        ) AS pending_out_amount
    FROM dms_parts.t_parts_sales_order so
    JOIN dms_parts.t_parts_sales_order_detail sod
        ON sod.order_id = so.id AND sod.del_flag = 0
    LEFT JOIN bo_cancel bc
        ON bc.order_detail_id = sod.id AND bc.part_no = sod.part_no
    LEFT JOIN dispatched d
        ON d.part_no = sod.part_no
    WHERE so.order_no = %(orderNo)s
        AND so.del_flag = 0
)
SELECT
    %(orderNo)s AS order_no,
    COALESCE(cf.frozen_amount, 0)      AS frozen_amount,
    COALESCE(cf.released_amount, 0)    AS released_amount,
    COALESCE(cf.used_amount, 0)        AS used_amount,
    COALESCE(pa.pending_out_amount, 0) AS pending_out_amount,
    COALESCE(cf.frozen_amount, 0)
    - COALESCE(cf.released_amount, 0)
    - COALESCE(cf.used_amount, 0)
    - COALESCE(pa.pending_out_amount, 0) AS diff_amount
FROM capital_flow_summary cf
CROSS JOIN pending_amount_summary pa
"""


def extract_order_numbers(file_path: str) -> list[str]:
    """从文件中提取所有销售订单号。"""
    order_nos = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 格式: "123\tORDER_NO -   ..."  或  "123\tORDER_NO - ..."
            # 用 tab 分割，取后半段，再用 " -" 分割取第一个字段
            if "\t" in line:
                _, rest = line.split("\t", 1)
            else:
                rest = line
            order_no = rest.split(" -", 1)[0].strip()
            if order_no:
                order_nos.append(order_no)
    return order_nos


def main():
    # ============================================================
    # 输入 / 输出路径（直接改这里）
    # ============================================================
    input_file = r"D:\__SYNC2\git-dms\mexico-dms-web-vue3\final_failed_orders_2026-05-10T16-51-59-099Z.txt"
    output_file = "order_capital_result.xlsx"

    if not os.path.exists(input_file):
        print(f"[错误] 文件不存在: {input_file}")
        sys.exit(1)

    order_nos = extract_order_numbers(input_file)
    print(f"共提取 {len(order_nos)} 个单号")

    # 去重
    unique_orders = list(dict.fromkeys(order_nos))
    if len(unique_orders) != len(order_nos):
        print(f"去重后 {len(unique_orders)} 个唯一单号")

    results = []
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            for i, order_no in enumerate(unique_orders, 1):
                print(f"[{i}/{len(unique_orders)}] 查询: {order_no}", end=" ... ")
                try:
                    cur.execute(SQL, {"orderNo": order_no})
                    row = cur.fetchone()
                    if row:
                        results.append({
                            "order_no": row[0],
                            "frozen_amount": float(row[1] or 0),
                            "released_amount": float(row[2] or 0),
                            "used_amount": float(row[3] or 0),
                            "pending_out_amount": float(row[4] or 0),
                            "diff_amount": float(row[5] or 0),
                        })
                        print(f"差额={row[5]}")
                    else:
                        results.append({
                            "order_no": order_no,
                            "frozen_amount": 0,
                            "released_amount": 0,
                            "used_amount": 0,
                            "pending_out_amount": 0,
                            "diff_amount": 0,
                        })
                        print("无结果")
                except Exception as e:
                    print(f"查询失败: {e}")
                    results.append({
                        "order_no": order_no,
                        "frozen_amount": None,
                        "released_amount": None,
                        "used_amount": None,
                        "pending_out_amount": None,
                        "diff_amount": None,
                        "error": str(e),
                    })
    finally:
        conn.close()

    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)
    print(f"\n结果已写入: {os.path.abspath(output_file)}")
    print(f"共 {len(results)} 行")


if __name__ == "__main__":
    main()
