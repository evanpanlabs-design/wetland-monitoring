"""
可视化模块
生成交互式网络图
"""

from pyvis.network import Network
from src import config
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def _get_hex_color(value, v_min, v_max):
    """
    热图颜色映射
    数值越高(污染) -> 红色；数值越低(清洁) -> 绿色
    """
    if value is None:
        return config.COLOR_UNSAMPLED
    
    # 归一化 (0.0 ~ 1.0)
    if v_max <= v_min:
        norm_val = 0.5
    else:
        norm_val = (value - v_min) / (v_max - v_min)
        norm_val = max(0, min(1, norm_val))
    
    # 颜色映射: High -> Red, Low -> Green
    map_pos = 1.0 - norm_val
    
    cmap = plt.get_cmap('RdYlGn')
    rgba = cmap(map_pos)
    return mcolors.to_hex(rgba)


def _inject_legend_html(html_path, v_min, v_max, indicator_name):
    """注入图例 HTML"""
    legend_html = f"""
    <div style="position: fixed; bottom: 30px; left: 20px; z-index: 9999; 
                background-color: rgba(255, 255, 255, 0.95); padding: 15px; 
                border-radius: 8px; border: 1px solid #ccc; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                font-family: 'Segoe UI', Arial, sans-serif; min-width: 130px;">
        <h4 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #333;">
            {indicator_name} (mg/L)
        </h4>
        <div style="display: flex; align-items: center; height: 160px;">
            <div style="width: 20px; height: 100%; 
                        background: linear-gradient(to top, #1a9850, #91cf60, #d9ef8b, #fee08b, #fc8d59, #d73027); 
                        margin-right: 12px; border: 1px solid #999; border-radius: 3px;"></div>
            <div style="display: flex; flex-direction: column; justify-content: space-between; 
                        height: 100%; font-size: 12px; color: #333; font-weight: 500;">
                <span>{v_max:.2f} (High)</span>
                <span>{(v_max + v_min) * 0.75:.2f}</span>
                <span>{(v_max + v_min) * 0.5:.2f}</span>
                <span>{(v_max + v_min) * 0.25:.2f}</span>
                <span>{v_min:.2f} (Low)</span>
            </div>
        </div>
    </div>
    """
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if '</body>' in content:
            new_content = content.replace('</body>', f'{legend_html}</body>')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
    except Exception as e:
        print(f"Legend injection failed: {e}")


def _inject_custom_styles(html_path):
    """注入自定义样式以美化界面"""
    custom_css = """
    <style>
        body {
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif !important;
        }
        .vis-network {
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .vis-tooltip {
            background-color: rgba(50, 50, 50, 0.9) !important;
            color: white !important;
            border-radius: 6px !important;
            padding: 10px !important;
            font-size: 13px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
        }
    </style>
    """
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if '</head>' in content:
            new_content = content.replace('</head>', f'{custom_css}</head>')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
    except Exception as e:
        print(f"Style injection failed: {e}")


def generate_interactive_network(
    model, 
    sampled_set=None, 
    heatmap_data=None, 
    v_min=0, 
    v_max=10, 
    indicator_name="Value",
    base_font_size=20
):
    """
    生成交互式网络图
    
    参数:
        model: WetlandSystem 模型实例
        sampled_set: 已采样节点集合 (用于采样状态视图)
        heatmap_data: 热图数据字典 {node_id: value}
        v_min, v_max: 热图颜色范围
        indicator_name: 指标名称
        base_font_size: 基础字体大小
    
    返回:
        str: 生成的 HTML 文件路径
    """
    net = Network(
        height="800px", 
        width="100%", 
        bgcolor="#f8f9fa", 
        font_color="black", 
        directed=True
    )
    
    for node in model.G.nodes():
        attr = model.G.nodes[node]
        gid = attr.get('Group_ID', 99)
        desc = attr.get('Description', '')
        
        # --- 样式逻辑 ---
        title_str = ""
        font_color = "#FFFFFF"
        
        if sampled_set is not None:
            # 采样状态视图
            if node in sampled_set:
                color = config.COLOR_SAMPLED
                title_str = "✅ 状态: 已采样"
            else:
                color = config.COLOR_UNSAMPLED
                title_str = "❌ 状态: 无数据"
                font_color = "#333333"
        
        elif heatmap_data is not None:
            # 热图视图
            val = heatmap_data.get(node)
            if val is not None:
                color = _get_hex_color(val, v_min, v_max)
                title_str = f"数值: {val:.3f} mg/L"
            else:
                color = config.COLOR_UNSAMPLED
                title_str = "无数据"
                font_color = "#333333"
        else:
            # 默认拓扑视图
            color = config.GROUP_COLORS.get(gid, '#999')
            title_str = f"分组: {gid}"
            if desc:
                title_str += f"\n描述: {desc}"
        
        # 形状与尺寸
        if node == 'Inlet':
            shape = 'circle'
            size = base_font_size * 2.0
            title_str = "🚰 总入水口\n" + title_str
        elif attr.get('Is_Outlet'):
            shape = 'diamond'
            size = base_font_size * 1.5
            title_str = "🔻 出水口\n" + title_str
        else:
            shape = 'box'
            size = base_font_size * 1.5
        
        # 标签
        label = node
        if heatmap_data and heatmap_data.get(node) is not None:
            label += f"\n{heatmap_data[node]:.2f}"
        
        net.add_node(
            node,
            label=label,
            title=title_str,
            color={
                'background': color, 
                'border': color, 
                'highlight': {'background': color, 'border': '#333333'}
            },
            shape=shape,
            size=size,
            level=model.node_levels.get(node, 0),
            font={
                'color': font_color,
                'size': base_font_size,
                'face': 'Arial',
                'bold': True,
                'vadjust': 0,
                'strokeWidth': 0
            },
            borderWidth=0,
            shadow={'enabled': True, 'size': 3, 'color': 'rgba(0,0,0,0.2)'},
            shapeProperties={
                'useImageSize': False,
                'useBorderWithImage': False,
                'borderRadius': 6
            }
        )
    
    # 添加边
    for src, tgt in model.G.edges():
        net.add_edge(
            src, tgt,
            color={'color': '#90A4AE', 'opacity': 0.6},
            width=2,
            arrowStrikethrough=False,
            smooth={
                'type': 'cubicBezier', 
                'forceDirection': 'vertical', 
                'roundness': 0.6
            }
        )
    
    # 设置布局选项
    net.set_options(f"""
    var options = {{
      "layout": {{
        "hierarchical": {{
          "enabled": true,
          "levelSeparation": {config.LEVEL_SEPARATION},
          "nodeSpacing": {config.NODE_SPACING},
          "treeSpacing": 220,
          "blockShifting": true,
          "edgeMinimization": true,
          "parentCentralization": true,
          "direction": "UD",
          "sortMethod": "directed",
          "shakeTowards": "roots"
        }}
      }},
      "physics": {{
        "hierarchicalRepulsion": {{
          "nodeDistance": {config.NODE_SPACING},
          "damping": 0.09
        }},
        "solver": "hierarchicalRepulsion"
      }},
      "interaction": {{
        "hover": true,
        "zoomView": true,
        "navigationButtons": true,
        "keyboard": {{
          "enabled": true
        }}
      }}
    }}
    """)
    
    output_path = os.path.join(config.BASE_DIR, "temp_network.html")
    net.save_graph(output_path)
    
    # 注入自定义样式
    _inject_custom_styles(output_path)
    
    # 如果是热图模式，注入图例
    if heatmap_data is not None:
        _inject_legend_html(output_path, v_min, v_max, indicator_name)
    
    return output_path