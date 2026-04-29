import os

# --- 路径配置 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# SQLite 数据库路径
DATABASE_PATH = os.path.join(DATA_DIR, 'wetland.db')

# --- 视觉配置 ---
COLOR_SAMPLED = '#1565C0'     # 蓝色 - 已采样
COLOR_UNSAMPLED = '#BDBDBD'   # 中灰 - 未采样
COLOR_TEXT = '#FFFFFF'        # 白字

# 分组颜色
GROUP_COLORS = {
    0: '#212121',   # Inlet (深黑)
    1: '#1565C0',   # 蓝色
    2: '#E65100',   # 深橙
    3: '#2E7D32',   # 深绿
    4: '#C62828',   # 深红
    99: '#607D8B'   # 蓝灰 (默认)
}

# --- PyVis 布局参数 ---
LEVEL_SEPARATION = 150
NODE_SPACING = 160

# --- 应用配置 ---
APP_TITLE = "海口凤翔湿地监测平台"
APP_ICON = ""
