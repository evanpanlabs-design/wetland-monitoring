# 海口凤翔湿地数字监测平台

基于 Streamlit 构建的人工湿地水质监测可视化平台，支持拓扑展示、采样监控、链路分析和全局热图等功能。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备数据

将 CSV 数据文件放入 `data/` 目录，然后运行迁移脚本：

```bash
python scripts/csv_to_sqlite.py
```

### 3. 启动应用

```bash
streamlit run app.py
```

## 项目结构

```
wetland-monitoring/
├── .streamlit/          # Streamlit 配置
├── data/                # 数据目录
│   └── wetland.db       # SQLite 数据库
├── src/                 # 源代码
│   ├── config.py        # 配置文件
│   ├── database.py      # 数据库模块
│   ├── data_loader.py   # 数据加载器
│   ├── model.py         # 业务模型
│   └── visualizer.py    # 可视化模块
├── scripts/             # 工具脚本
├── app.py               # 主应用
└── requirements.txt     # 依赖列表
```

## 技术栈

- **前端**: Streamlit, PyVis, Plotly
- **后端**: Python, NetworkX
- **数据库**: SQLite
- **部署**: Streamlit Cloud

## 功能模块

| 模块 | 功能描述 |
|------|----------|
| 物理拓扑 | 展示湿地各单元的连接关系和层级结构 |
| 采样监控 | 按日期查看采样点位分布，显示采样覆盖率统计 |
| 链路分析 | 分析污染物沿水流路径的浓度变化 |
| 全局热图 | 显示各监测点的浓度分布热图 |

## Streamlit Cloud 部署

### 步骤 1: 准备 GitHub 仓库

```bash
# 1. 初始化 Git 仓库
cd wetland-monitoring
git init

# 2. 添加所有文件
git add .

# 3. 首次提交
git commit -m "Initial commit: 湿地监测平台 v2.1"

# 4. 创建 GitHub 仓库（在 GitHub 网站上操作）

# 5. 关联远程仓库
git remote add origin https://github.com/你的用户名/wetland-monitoring.git

# 6. 推送代码
git branch -M main
git push -u origin main
```

### 步骤 2: 数据迁移（本地执行）

```bash
# 1. 确保 CSV 文件在 data/ 目录下
# - data/Master_GlobalUID.csv
# - data/Connections.csv
# - data/Measurements.csv

# 2. 运行迁移脚本
python scripts/csv_to_sqlite.py

# 3. 验证数据库生成成功
# 检查 data/wetland.db 文件是否存在

# 4. 将数据库添加到 Git
git add data/wetland.db
git commit -m "Add SQLite database"
git push
```

### 步骤 3: 部署到 Streamlit Cloud

1. 访问 https://share.streamlit.io/
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择仓库、分支、主文件路径 (app.py)
5. 点击 "Deploy!"

## 常见问题

### Q1: 数据库文件太大无法推送
```bash
git lfs install
git lfs track "*.db"
git add .gitattributes
git commit -m "Enable Git LFS for database"
```

### Q2: 部署后显示"数据库未找到"
- 确保 `data/wetland.db` 已提交到仓库
- 检查 `.gitignore` 没有忽略 `.db` 文件

## License

MIT License
