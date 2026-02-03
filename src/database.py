"""
数据库管理模块
提供 SQLite 数据库的连接和查询功能
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager
from src import config
import streamlit as st


class DatabaseManager:
    """SQLite 数据库管理器"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or config.DATABASE_PATH
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # 支持字典式访问
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        """执行查询并返回 DataFrame"""
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def execute_scalar(self, query, params=None):
        """执行查询并返回单个值"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            result = cursor.fetchone()
            return result[0] if result else None
    
    # ============ 节点查询 ============
    def get_all_units(self):
        """获取所有节点信息"""
        query = """
            SELECT 
                global_uid as Global_UID,
                group_id as Group_ID,
                id_2025 as "2025_ID",
                original_label as Original_Label,
                is_outlet as Is_Outlet,
                unit_type as Unit_Type,
                id_2018 as "2018_ID",
                description as Description
            FROM units
            ORDER BY group_id, id_2025
        """
        df = self.execute_query(query)
        # 转换布尔值
        df['Is_Outlet'] = df['Is_Outlet'].astype(bool)
        return df
    
    def get_outlets(self):
        """获取所有出水口节点"""
        query = "SELECT global_uid FROM units WHERE is_outlet = 1"
        df = self.execute_query(query)
        return df['global_uid'].tolist()
    
    # ============ 连接关系查询 ============
    def get_all_connections(self):
        """获取所有连接关系"""
        query = """
            SELECT 
                source_uid as Source_UID,
                target_uid as Target_UID
            FROM connections
        """
        return self.execute_query(query)
    
    # ============ 监测数据查询 ============
    def get_all_measurements(self):
        """获取所有监测数据"""
        query = """
            SELECT 
                date as Date,
                global_uid as Global_UID,
                indicator as Indicator,
                value as Value,
                error as Error,
                unit as Unit,
                note as Note
            FROM measurements
            ORDER BY date, global_uid
        """
        df = self.execute_query(query)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    
    def get_available_dates(self):
        """获取所有可用的采样日期"""
        query = "SELECT DISTINCT date FROM measurements ORDER BY date"
        df = self.execute_query(query)
        return pd.to_datetime(df['date']).dt.date.tolist()
    
    def get_available_indicators(self):
        """获取所有可用的监测指标"""
        query = "SELECT DISTINCT indicator FROM measurements ORDER BY indicator"
        df = self.execute_query(query)
        return df['indicator'].tolist()
    
    def get_measurements_by_date(self, date):
        """获取指定日期的监测数据"""
        query = """
            SELECT 
                global_uid as Global_UID,
                indicator as Indicator,
                value as Value
            FROM measurements
            WHERE date = ?
        """
        return self.execute_query(query, (str(date),))
    
    def get_measurements_by_date_indicator(self, date, indicator):
        """获取指定日期和指标的监测数据"""
        query = """
            SELECT 
                global_uid as Global_UID,
                value as Value
            FROM measurements
            WHERE date = ? AND indicator = ?
        """
        return self.execute_query(query, (str(date), indicator))
    
    def get_sampled_nodes(self, date):
        """获取指定日期采样的节点列表"""
        query = """
            SELECT DISTINCT global_uid 
            FROM measurements 
            WHERE date = ?
        """
        df = self.execute_query(query, (str(date),))
        return set(df['global_uid'].tolist())
    
    def get_indicator_stats(self, indicator):
        """获取指定指标的统计信息（用于热图颜色范围）"""
        query = """
            SELECT 
                MIN(value) as min_val,
                MAX(value) as max_val,
                AVG(value) as avg_val
            FROM measurements
            WHERE indicator = ?
        """
        df = self.execute_query(query, (indicator,))
        if df.empty:
            return 0, 10, 5
        row = df.iloc[0]
        return row['min_val'], row['max_val'], row['avg_val']
    
    def get_indicator_percentiles(self, indicator, lower=0.05, upper=0.95):
        """获取指定指标的分位数（用于热图颜色范围）"""
        query = f"""
            SELECT value FROM measurements 
            WHERE indicator = ? AND value IS NOT NULL
            ORDER BY value
        """
        df = self.execute_query(query, (indicator,))
        if df.empty or len(df) < 2:
            return 0, 10
        
        values = df['value'].values
        v_min = values[int(len(values) * lower)]
        v_max = values[int(len(values) * upper)]
        return float(v_min), float(v_max)
    
    # ============ 统计查询 ============
    def get_daily_summary(self, date):
        """获取指定日期的采样摘要"""
        query = """
            SELECT 
                indicator,
                COUNT(*) as sample_count,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value
            FROM measurements
            WHERE date = ?
            GROUP BY indicator
        """
        return self.execute_query(query, (str(date),))
    
    def get_node_count(self):
        """获取节点总数"""
        return self.execute_scalar("SELECT COUNT(*) FROM units")
    
    def get_connection_count(self):
        """获取连接总数"""
        return self.execute_scalar("SELECT COUNT(*) FROM connections")


# 单例模式 - 全局数据库管理器
@st.cache_resource
def get_db_manager():
    """获取数据库管理器单例"""
    return DatabaseManager()