"""按单号查询销售订单资金情况，输出执行日志。

将 SQL 逐行执行，每个 SQL 期望只返回 1 条记录。
若返回 0 条或大于 1 条，则在控制台打印醒目的错误提示。
所有 SQL 语句及查询结果写入日志文件，控制台不打印其他干扰信息。
"""

import os
import sys
from datetime import datetime

import pymysql

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


sql = """
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI250201202506250003%' AND amount=555.98 AND operate_date BETWEEN '2026-06-08 11:51:51' AND '2026-06-08 11:51:53' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI101701202503260003%' AND amount=3590.36 AND operate_date BETWEEN '2026-06-08 11:59:40' AND '2026-06-08 11:59:42' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI291303202505070011%' AND amount=92.6 AND operate_date BETWEEN '2026-06-08 12:00:11' AND '2026-06-08 12:00:13' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI291303202505070011%' AND amount=2900.79 AND operate_date BETWEEN '2026-06-08 11:57:25' AND '2026-06-08 11:57:27' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI261401202507010001%' AND amount=15868.49 AND operate_date BETWEEN '2026-06-08 12:00:48' AND '2026-06-08 12:00:50' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI191204202506250005%' AND amount=9561.44 AND operate_date BETWEEN '2026-06-08 12:03:21' AND '2026-06-08 12:03:23' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI182301202505130001%' AND amount=0.5 AND operate_date BETWEEN '2026-06-08 12:03:30' AND '2026-06-08 12:03:32' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI111603202505100001%' AND amount=5282.46 AND operate_date BETWEEN '2026-06-08 12:03:50' AND '2026-06-08 12:03:52' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI050102202505090001%' AND amount=1136.63 AND operate_date BETWEEN '2026-06-08 11:59:21' AND '2026-06-08 11:59:23' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI152606202504240006%' AND amount=1909.39 AND operate_date BETWEEN '2026-06-08 12:03:38' AND '2026-06-08 12:03:40' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI152606202503120001%' AND amount=762.78 AND operate_date BETWEEN '2026-06-08 12:03:41' AND '2026-06-08 12:03:43' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI113304202502240001%' AND amount=124.18 AND operate_date BETWEEN '2026-06-08 11:59:44' AND '2026-06-08 11:59:46' limit 50;
SELECT * FROM dms_retail.tt_capital_flow WHERE order_no like '%SGACI232601202502150001%' AND amount=100.22 AND operate_date BETWEEN '2026-06-08 11:59:17' AND '2026-06-08 11:59:19' limit 50;
"""

# 查询 SQL（每行为一个独立 SQL）
SQL_LIST = sql.split("\n")

LOG_FILE = "query_execution_log.txt"


def main():
    conn = pymysql.connect(**DB_CONFIG)
    log_lines = []
    log_lines.append(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append(f"SQL 总数: {len(SQL_LIST)}")
    log_lines.append("-" * 60)

    try:
        with conn.cursor() as cur:
            for i, sql in enumerate(SQL_LIST, 1):
                if sql == "":
                    continue
                log_lines.append(f"\n[SQL {i}]\n{sql}")
                try:
                    cur.execute(sql)
                    rows = cur.fetchall()
                    row_count = len(rows)
                    log_lines.append(f"结果条数: {row_count}")

                    if row_count == 1:
                        log_lines.append(f"查询结果:\n{rows[0]}")
                    else:
                        log_lines.append(f"查询结果:\n{rows}")

                        # 控制台打印醒目错误提示
                        print("=" * 60)
                        print(f"[错误] SQL {i} 查询结果异常！期望 1 条，实际 {row_count} 条")
                        print(f"SQL: {sql}")
                        print("=" * 60)

                except Exception as e:
                    log_lines.append(f"执行异常: {e}")
                    print("=" * 60)
                    print(f"[错误] SQL {i} 执行失败！")
                    print(f"SQL: {sql}")
                    print(f"异常: {e}")
                    print("=" * 60)

    finally:
        conn.close()

    # 写入日志文件
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"\n执行日志已写入: {os.path.abspath(LOG_FILE)}")


if __name__ == "__main__":
    main()
