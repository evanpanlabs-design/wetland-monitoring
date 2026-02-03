"""
数据加载器
从 SQLite 数据库加载数据，保持与原有接口的兼容性
"""

import pandas as pd
import streamlit as st
from src.database import get_db_manager


class DataLoader:
    """数据加载器 - 从 SQLite 数据库加载数据"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.master = None
        self.conn = None
        self.meas = None
    
    @st.cache_data(ttl=300)  # 缓存5分钟
    def load_all(_self):
        """
        加载所有数据
        返回: (master_df, conn_df, meas_df) 或 (None, None, None) 如果失败
        """
        try:
            # 1. 加载节点主表
            _self.master = _self.db.get_all_units()
            if _self.master is None or _self.master.empty:
                st.error("❌ 无法加载节点数据 (units 表)")
                return None, None, None
            
            # 确保 Global_UID 是字符串
            _self.master['Global_UID'] = _self.master['Global_UID'].astype(str)
            
            # 2. 加载连接关系表
            _self.conn = _self.db.get_all_connections()
            if _self.conn is None or _self.conn.empty:
                st.error("❌ 无法加载连接数据 (connections 表)")
                return None, None, None
            
            _self.conn['Source_UID'] = _self.conn['Source_UID'].astype(str)
            _self.conn['Target_UID'] = _self.conn['Target_UID'].astype(str)
            
            # 3. 加载监测数据表
            _self.meas = _self.db.get_all_measurements()
            if _self.meas is None or _self.meas.empty:
                st.warning("⚠️ 监测数据表为空")
                # 创建空的 DataFrame 以保持兼容性
                _self.meas = pd.DataFrame(columns=['Date', 'Global_UID', 'Indicator', 'Value', 'Error', 'Unit', 'Note'])
            else:
                _self.meas['Global_UID'] = _self.meas['Global_UID'].astype(str)
            
            return _self.master, _self.conn, _self.meas
        
        except Exception as e:
            st.error(f"❌ 数据加载失败: {e}")
            return None, None, None
    
    def get_available_dates(self):
        """获取可用的采样日期列表"""
        return self.db.get_available_dates()
    
    def get_available_indicators(self):
        """获取可用的监测指标列表"""
        return self.db.get_available_indicators()