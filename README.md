# 🌿 海口凤翔湿地数字监测平台

基于 Streamlit 构建的人工湿地水质监测可视化平台，支持拓扑展示、采样监控、链路分析和全局热图等功能。

## 🚀 快速开始

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

## 📁 项目结构

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

## 🔧 技术栈

- **前端**: Streamlit, PyVis, Plotly
- **后端**: Python, NetworkX
- **数据库**: SQLite
- **部署**: Streamlit Cloud

## 📝 License

MIT License
```

## 三、Streamlit Cloud 部署 SOP

### 步骤 1: 准备 GitHub 仓库

```bash
# 1. 初始化 Git 仓库
cd wetland-monitoring
git init

# 2. 添加所有文件
git add .

# 3. 首次提交
git commit -m "Initial commit: 湿地监测平台 v2.0"

# 4. 创建 GitHub 仓库（在 GitHub 网站上操作）
# 仓库名建议: wetland-monitoring

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

1. **访问 Streamlit Cloud**
   - 打开 https://share.streamlit.io/
   - 使用 GitHub 账号登录

2. **创建新应用**
   - 点击 "New app"
   - 选择仓库: `你的用户名/wetland-monitoring`
   - 选择分支: `main`
   - 主文件路径: `app.py`

3. **配置设置**
   - Python 版本: 3.9 或 3.10
   - 点击 "Deploy!"

4. **等待部署**
   - 通常需要 2-5 分钟
   - 可以在日志中查看部署进度

5. **获取访问链接**
   - 部署成功后，获得类似链接:
   - `https://你的用户名-wetland-monitoring-app-xxxxx.streamlit.app`

### 步骤 4: 后续更新

```bash
# 每次修改代码后
git add .
git commit -m "更新描述"
git push

# Streamlit Cloud 会自动检测并重新部署
```

## 四、常见问题解决

### Q1: 数据库文件太大无法推送
```bash
# 使用 Git LFS
git lfs install
git lfs track "*.db"
git add .gitattributes
git commit -m "Enable Git LFS for database"
```

### Q2: 部署后显示"数据库未找到"
- 确保 `data/wetland.db` 已提交到仓库
- 检查 `.gitignore` 没有忽略 `.db` 文件

### Q3: 内存不足错误
- 在 `app.py` 中减少缓存数据量
- 使用 `st.cache_data(ttl=300)` 限制缓存时间

### Q4: 页面加载缓慢
- 考虑对大型数据集进行分页
- 使用数据库索引优化查询

## 五、验证清单

- [ ] CSV 文件格式正确
- [ ] 运行迁移脚本成功
- [ ] `wetland.db` 生成在 `data/` 目录
- [ ] 本地 `streamlit run app.py` 正常运行
- [ ] 代码已推送到 GitHub
- [ ] Streamlit Cloud 部署成功
- [ ] 在线访问正常