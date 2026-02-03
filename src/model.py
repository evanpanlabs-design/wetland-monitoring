"""
湿地系统业务模型
包含网络图构建、路径分析等核心逻辑
"""

import networkx as nx
import pandas as pd
import numpy as np
from src import config
from src.database import get_db_manager


class WetlandSystem:
    """湿地系统模型"""
    
    def __init__(self, master_df, conn_df, meas_df):
        self.master = master_df
        self.conn = conn_df
        self.meas = meas_df
        self.db = get_db_manager()
        self.G = nx.DiGraph()
        self.node_levels = {}
        
        self._build_graph()
        self._calculate_levels()
    
    def _build_graph(self):
        """构建有向图"""
        # 添加节点
        for _, row in self.master.iterrows():
            uid = str(row['Global_UID']).strip()
            self.G.add_node(uid, **row.to_dict())
        
        # 添加边
        for _, row in self.conn.iterrows():
            src = str(row['Source_UID']).strip()
            tgt = str(row['Target_UID']).strip()
            if src in self.G and tgt in self.G:
                self.G.add_edge(src, tgt)
    
    def _calculate_levels(self):
        """计算节点层级（用于分层布局）"""
        levels = {}
        if 'Inlet' in self.G:
            try:
                levels = dict(nx.shortest_path_length(self.G, source='Inlet'))
            except nx.NetworkXError:
                levels = {n: 0 for n in self.G.nodes()}
        
        max_level = max(levels.values()) if levels else 0
        for node in self.G.nodes():
            if node not in levels:
                levels[node] = max_level + 1
        
        self.node_levels = levels
    
    def get_sampling_status(self, target_date):
        """获取指定日期的采样状态（使用数据库查询）"""
        if target_date is None:
            return set()
        return self.db.get_sampled_nodes(target_date)
    
    def get_pollutant_heatmap(self, selected_date, indicator):
        """获取指定日期和指标的污染物热图数据"""
        df = self.db.get_measurements_by_date_indicator(selected_date, indicator)
        if df.empty:
            return {}
        return df.groupby('Global_UID')['Value'].mean().astype(float).to_dict()
    
    def get_path_profile(self, target_outlet, date, indicator):
        """
        获取从入口到指定出口的路径剖面数据
        返回包含所有可能路径的 DataFrame
        """
        if 'Inlet' not in self.G or target_outlet not in self.G:
            return None
        
        try:
            paths = list(nx.all_simple_paths(self.G, 'Inlet', target_outlet))
        except nx.NetworkXError:
            return None
        
        if not paths:
            return None
        
        # 获取数据
        data_map = self.get_pollutant_heatmap(date, indicator)
        
        results = []
        for path_idx, path in enumerate(paths):
            path_id = f"Path {path_idx + 1}"
            
            for step, node_uid in enumerate(path):
                val = data_map.get(node_uid, np.nan)
                results.append({
                    'Step': step,
                    'Value': val,
                    'Global_UID': node_uid,
                    'Path_ID': path_id
                })
        
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by=['Path_ID', 'Step'])
        
        return df
    
    def get_outlets(self):
        """获取所有出水口节点"""
        return [n for n, d in self.G.nodes(data=True) if d.get('Is_Outlet')]
    
    def get_node_info(self, node_id):
        """获取指定节点的详细信息"""
        if node_id in self.G:
            return dict(self.G.nodes[node_id])
        return None