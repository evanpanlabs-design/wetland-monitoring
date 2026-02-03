"""
CSV 转 SQLite 迁移脚本
运行方式: python scripts/csv_to_sqlite.py
"""

import sqlite3
import pandas as pd
import os
import sys

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# 输入 CSV 文件路径
CSV_MASTER = os.path.join(DATA_DIR, 'Master_GlobalUID.csv')
CSV_CONN = os.path.join(DATA_DIR, 'Connections.csv')
CSV_MEAS = os.path.join(DATA_DIR, 'Measurements.csv')

# 输出 SQLite 数据库路径
DB_PATH = os.path.join(DATA_DIR, 'wetland.db')


def read_csv_with_fallback(file_path):
    """尝试多种编码读取CSV"""
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb18030', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            df.columns = df.columns.str.strip()
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            print(f"  ✓ 成功读取: {os.path.basename(file_path)} (编码: {enc})")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"  ✗ 读取失败 ({enc}): {e}")
            continue
    raise ValueError(f"无法读取文件: {file_path}")


def create_database():
    """创建SQLite数据库并导入数据"""
    
    # 删除旧数据库（如果存在）
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"已删除旧数据库: {DB_PATH}")
    
    # 创建新数据库连接
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📦 开始创建数据库...")
    
    # ============ 1. 创建 Master 表 ============
    print("\n[1/3] 创建 units 表 (节点主表)...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS units (
            global_uid TEXT PRIMARY KEY,
            group_id INTEGER,
            id_2025 INTEGER,
            original_label TEXT,
            is_outlet INTEGER DEFAULT 0,
            unit_type TEXT,
            id_2018 INTEGER,
            description TEXT
        )
    ''')
    
    df_master = read_csv_with_fallback(CSV_MASTER)
    # 字段映射
    column_mapping = {
        'Global_UID': 'global_uid',
        'Group_ID': 'group_id',
        '2025_ID': 'id_2025',
        'Original_Label': 'original_label',
        'Is_Outlet': 'is_outlet',
        'Unit_Type': 'unit_type',
        '2018_ID': 'id_2018',
        'Description': 'description'
    }
    df_master = df_master.rename(columns=column_mapping)
    
    # 处理布尔值
    if 'is_outlet' in df_master.columns:
        df_master['is_outlet'] = df_master['is_outlet'].apply(
            lambda x: 1 if str(x).upper() in ['TRUE', '1', 'YES'] else 0
        )
    
    df_master.to_sql('units', conn, if_exists='replace', index=False)
    print(f"  ✓ 导入 {len(df_master)} 条节点记录")
    
    # ============ 2. 创建 Connections 表 ============
    print("\n[2/3] 创建 connections 表 (连接关系表)...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_uid TEXT NOT NULL,
            target_uid TEXT NOT NULL,
            FOREIGN KEY (source_uid) REFERENCES units(global_uid),
            FOREIGN KEY (target_uid) REFERENCES units(global_uid)
        )
    ''')
    
    df_conn = read_csv_with_fallback(CSV_CONN)
    # 兼容旧列名
    if 'From' in df_conn.columns:
        df_conn = df_conn.rename(columns={'From': 'Source_UID', 'To': 'Target_UID'})
    
    column_mapping = {
        'Source_UID': 'source_uid',
        'Target_UID': 'target_uid'
    }
    df_conn = df_conn.rename(columns=column_mapping)
    df_conn.to_sql('connections', conn, if_exists='replace', index=False)
    print(f"  ✓ 导入 {len(df_conn)} 条连接记录")
    
    # ============ 3. 创建 Measurements 表 ============
    print("\n[3/3] 创建 measurements 表 (监测数据表)...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            global_uid TEXT NOT NULL,
            indicator TEXT NOT NULL,
            value REAL,
            error REAL,
            unit TEXT,
            note TEXT,
            FOREIGN KEY (global_uid) REFERENCES units(global_uid)
        )
    ''')
    
    # 创建索引以加速查询
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meas_date ON measurements(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meas_uid ON measurements(global_uid)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meas_indicator ON measurements(indicator)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meas_date_indicator ON measurements(date, indicator)')
    
    df_meas = read_csv_with_fallback(CSV_MEAS)
    column_mapping = {
        'Date': 'date',
        'Global_UID': 'global_uid',
        'Indicator': 'indicator',
        'Value': 'value',
        'Error': 'error',
        'Unit': 'unit',
        'Note': 'note'
    }
    df_meas = df_meas.rename(columns=column_mapping)
    
    # 确保日期格式统一
    df_meas['date'] = pd.to_datetime(df_meas['date']).dt.strftime('%Y-%m-%d')
    
    df_meas.to_sql('measurements', conn, if_exists='replace', index=False)
    print(f"  ✓ 导入 {len(df_meas)} 条监测记录")
    
    # ============ 4. 创建视图 ============
    print("\n[额外] 创建便捷查询视图...")
    
    # 视图1: 带节点信息的监测数据
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_measurements_with_units AS
        SELECT 
            m.*,
            u.group_id,
            u.is_outlet,
            u.description
        FROM measurements m
        LEFT JOIN units u ON m.global_uid = u.global_uid
    ''')
    
    # 视图2: 各日期各指标的统计摘要
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_daily_summary AS
        SELECT 
            date,
            indicator,
            COUNT(*) as sample_count,
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value
        FROM measurements
        GROUP BY date, indicator
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 数据库创建成功: {DB_PATH}")
    print(f"   文件大小: {os.path.getsize(DB_PATH) / 1024:.1f} KB")
    
    # 验证
    verify_database()


def verify_database():
    """验证数据库完整性"""
    print("\n🔍 验证数据库...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查各表记录数
    tables = ['units', 'connections', 'measurements']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} 条记录")
    
    # 检查指标类型
    cursor.execute("SELECT DISTINCT indicator FROM measurements")
    indicators = [row[0] for row in cursor.fetchall()]
    print(f"  监测指标: {', '.join(indicators)}")
    
    # 检查日期范围
    cursor.execute("SELECT MIN(date), MAX(date) FROM measurements")
    date_range = cursor.fetchone()
    print(f"  日期范围: {date_range[0]} ~ {date_range[1]}")
    
    conn.close()
    print("\n✅ 数据库验证通过!")


if __name__ == '__main__':
    print("=" * 50)
    print("   CSV → SQLite 数据迁移工具")
    print("=" * 50)
    
    # 检查 CSV 文件是否存在
    csv_files = [CSV_MASTER, CSV_CONN, CSV_MEAS]
    missing = [f for f in csv_files if not os.path.exists(f)]
    
    if missing:
        print("\n❌ 缺少以下 CSV 文件:")
        for f in missing:
            print(f"   - {f}")
        sys.exit(1)
    
    create_database()