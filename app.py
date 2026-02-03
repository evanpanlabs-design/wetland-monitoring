"""
海口凤翔湿地数字监测平台 - 主应用
"""

import streamlit as st
import streamlit.components.v1 as components
from src.data_loader import DataLoader
from src.model import WetlandSystem
from src.visualizer import generate_interactive_network
from src.database import get_db_manager
from src import config
import plotly.express as px
import plotly.graph_objects as go
import os

# ============ 页面配置 ============
st.set_page_config(
    page_title="海口凤翔湿地数字孪生",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# ============ 自定义样式 ============
st.markdown("""
<style>
    /* 主容器样式 */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* 标题样式 */
    h1 {
        color: #1B5E20;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E8F5E9 0%, #C8E6C9 100%);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #2E7D32;
    }
    
    /* 选项卡样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E8F5E9;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        color: #2E7D32;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E7D32 !important;
        color: white !important;
    }
    
    /* 指标卡片样式 */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #1B5E20;
    }
    
    /* 下载按钮样式 */
    .stDownloadButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    
    .stDownloadButton > button:hover {
        background-color: #388E3C;
    }
    
    /* 信息框样式 */
    .stAlert {
        border-radius: 10px;
    }
    
    /* 图表容器样式 */
    .plot-container {
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============ 数据加载 ============
@st.cache_resource
def load_system():
    """加载并缓存系统数据"""
    loader = DataLoader()
    master, conn, meas = loader.load_all()
    if master is None:
        return None, None
    system = WetlandSystem(master, conn, meas)
    return loader, system

loader, sys = load_system()

if sys is None:
    st.error("❌ 系统初始化失败，请检查数据库文件是否存在。")
    st.info("💡 请确保 `data/wetland.db` 文件存在。如果没有，请先运行 `python scripts/csv_to_sqlite.py` 进行数据迁移。")
    st.stop()

db = get_db_manager()

# ============ 侧边栏 ============
st.sidebar.markdown("## 🎛️ 监测控制台")

# 视觉设置
with st.sidebar.expander("👁️ 视觉设置", expanded=False):
    font_size = st.slider("节点字号", min_value=10, max_value=40, value=18, step=2)

st.sidebar.divider()

# 日期选择
available_dates = db.get_available_dates()
if available_dates:
    selected_date = st.sidebar.selectbox(
        "📅 选择采样日期",
        available_dates,
        index=len(available_dates) - 1,
        format_func=lambda x: x.strftime('%Y年%m月%d日')
    )
else:
    selected_date = None
    st.sidebar.warning("暂无采样数据")

# 指标选择
available_indicators = db.get_available_indicators()
if available_indicators:
    selected_indicator = st.sidebar.selectbox(
        "🧪 选择监测指标",
        available_indicators
    )
else:
    selected_indicator = None

st.sidebar.divider()

# 系统信息
st.sidebar.markdown("### 📊 系统信息")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("节点数", len(sys.G.nodes))
with col2:
    st.metric("连接数", len(sys.G.edges))

# 版本信息
st.sidebar.markdown("---")
st.sidebar.caption("🌿 海口凤翔湿地监测平台 v2.0")
st.sidebar.caption("基于 Streamlit + SQLite 构建")

# ============ 主内容区 ============
st.markdown("# 🌿 海口凤翔湿地数字监测平台")
st.markdown("*实时监测人工湿地水质变化，助力生态环境保护*")

# 渲染函数
def render_html_with_download(file_path, download_name="network_graph.html"):
    """渲染 HTML 并提供下载按钮"""
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    col_dl, col_info = st.columns([1, 5])
    with col_dl:
        st.download_button(
            label="💾 导出视图",
            data=html_content,
            file_name=download_name,
            mime="text/html",
            help="下载为离线 HTML 文件，可用浏览器直接打开"
        )
    
    components.html(html_content, height=820, scrolling=False)

# ============ 选项卡 ============
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ 物理拓扑",
    "🧪 采样监控",
    "📈 链路分析",
    "🌡️ 全局热图"
])

with tab1:
    st.markdown("### 🗺️ 系统物理拓扑")
    st.markdown("*展示湿地各单元的连接关系和层级结构*")
    
    with st.spinner("正在生成拓扑图..."):
        path = generate_interactive_network(sys, base_font_size=font_size)
        render_html_with_download(path, "topology_map.html")

with tab2:
    if selected_date:
        st.markdown(f"### 🧪 {selected_date.strftime('%Y年%m月%d日')} 采样点位分布")
        
        sampled_nodes = sys.get_sampling_status(selected_date)
        total_nodes = len(sys.G.nodes) - 1  # 排除 Inlet
        coverage = len(sampled_nodes) / total_nodes if total_nodes > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("采样节点数", f"{len(sampled_nodes)}")
        with col2:
            st.metric("总节点数", f"{total_nodes}")
        with col3:
            st.metric("覆盖率", f"{coverage:.1%}")
        
        with st.spinner("正在生成采样分布图..."):
            path = generate_interactive_network(
                sys,
                sampled_set=sampled_nodes,
                base_font_size=font_size
            )
            render_html_with_download(path, f"sampling_{selected_date}.html")
    else:
        st.info("请在侧边栏选择采样日期")

with tab3:
    st.markdown("### 📈 链路剖面分析")
    st.markdown("*分析污染物沿水流路径的浓度变化*")
    
    outlets = sys.get_outlets()
    
    if outlets and selected_date and selected_indicator:
        col1, col2 = st.columns([1, 3])
        with col1:
            target_out = st.selectbox("选择目标出水口", outlets)
        
        if target_out:
            df_profile = sys.get_path_profile(target_out, selected_date, selected_indicator)
            
            if df_profile is not None and not df_profile.empty and df_profile['Value'].count() > 0:
                # 使用 Plotly 绘制折线图
                fig = px.line(
                    df_profile,
                    x='Step',
                    y='Value',
                    color='Path_ID',
                    markers=True,
                    hover_data=['Global_UID'],
                    title=f"{selected_indicator} 沿程变化 (入口 → {target_out})"
                )
                
                fig.update_traces(
                    connectgaps=True,
                    line=dict(width=3),
                    marker=dict(size=10)
                )
                
                fig.update_layout(
                    height=500,
                    xaxis_title="流程步长 (Step)",
                    yaxis_title=f"{selected_indicator} (mg/L)",
                    legend_title="路径",
                    font=dict(size=14),
                    hovermode='x unified',
                    plot_bgcolor='rgba(248,249,250,1)',
                    paper_bgcolor='rgba(248,249,250,1)'
                )
                
                fig.update_xaxes(gridcolor='rgba(0,0,0,0.1)', tickmode='linear')
                fig.update_yaxes(gridcolor='rgba(0,0,0,0.1)')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 显示数据表
                with st.expander("📋 查看原始数据"):
                    st.dataframe(
                        df_profile.pivot(index='Step', columns='Path_ID', values='Value'),
                        use_container_width=True
                    )
            else:
                st.warning("⚠️ 该日期/指标暂无数据，或路径不可达。")
    else:
        st.info("请在侧边栏选择日期和指标")

with tab4:
    if selected_date and selected_indicator:
        st.markdown(f"### 🌡️ {selected_indicator} 全局热图")
        st.markdown(f"*{selected_date.strftime('%Y年%m月%d日')} 各监测点浓度分布*")
        
        # 获取颜色范围
        vmin, vmax = db.get_indicator_percentiles(selected_indicator)
        if vmax == vmin:
            vmax += 0.1
        
        # 获取热图数据
        data_map = sys.get_pollutant_heatmap(selected_date, selected_indicator)
        
        if data_map:
            # 显示统计信息
            values = list(data_map.values())
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("监测点数", len(values))
            with col2:
                st.metric("最小值", f"{min(values):.2f}")
            with col3:
                st.metric("最大值", f"{max(values):.2f}")
            with col4:
                st.metric("平均值", f"{sum(values)/len(values):.2f}")
        
        with st.spinner("正在生成热图..."):
            path = generate_interactive_network(
                sys,
                heatmap_data=data_map,
                v_min=vmin,
                v_max=vmax,
                indicator_name=selected_indicator,
                base_font_size=font_size
            )
            render_html_with_download(path, f"heatmap_{selected_indicator}_{selected_date}.html")
    else:
        st.info("请在侧边栏选择日期和指标")

# ============ 页脚 ============
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 12px;">
        🌿 海口凤翔湿地数字监测平台 | 
        数据来源: 实地监测 | 
        技术支持: Streamlit + SQLite + NetworkX
    </div>
    """,
    unsafe_allow_html=True
)