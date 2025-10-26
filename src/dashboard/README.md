# Bitcoin Research Agent Dashboard

## 📊 可视化仪表板

交互式Web应用，展示比特币市场分析结果。

## 🚀 快速启动

### Windows
```bash
run_dashboard.bat
```

### Linux/Mac
```bash
streamlit run src/dashboard/app.py
```

## 📱 访问

浏览器自动打开：`http://localhost:8501`

## 📖 页面说明

### 1. 🏠 市场概览
- **关键指标**：价格、市场状态、波动率、情绪、资金流
- **价格走势图**：结合市场状态背景
- **市场统计**：最近30天的各项统计
- **主力行为分布**：饼图展示

### 2. 📈 市场状态
- **状态分布**：4种市场状态的天数统计
- **状态特征对比**：各状态的平均收益率、波动率、情绪
- **状态转移矩阵**：热力图展示状态转移概率

### 3. 📉 波动率分析
- **波动率时间序列**：多时间窗口波动率走势
- **波动率锥形图**：历史波动率分布与当前值对比
- **波动率统计**：各时间窗口的波动率数据

### 4. 😊 情绪指数
- **当前情绪**：Fear & Greed Index 大数字展示
- **历史走势**：F&G指数时间序列
- **情绪分布**：饼图展示各情绪等级占比
- **情绪vs价格**：双图对比

### 5. 💰 资金流向
- **关键指标**：鲸鱼活动、主力行为、MFI、鲸鱼频率
- **资金流向时间序列**：正负资金流柱状图
- **主力行为分布**：各行为天数统计
- **鲸鱼活动趋势**：7天滚动频率
- **资金异动事件**：最近10次异动详情

### 6. 🎯 综合信号
- **综合评分**：多维度信号打分（-8 ~ +8）
- **信号详情**：各指标贡献及建议
- **操作建议**：基于评分的具体建议
- **历史回测**：信号准确率统计

## 🎨 特点

- ✅ **实时数据**：自动加载最新分析结果
- ✅ **交互式图表**：Plotly交互式可视化
- ✅ **响应式布局**：适配不同屏幕尺寸
- ✅ **数据缓存**：5分钟缓存提升性能
- ✅ **中文界面**：完整中文支持
- ✅ **美观设计**：专业的配色和布局

## 📦 依赖

```bash
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
numpy>=1.24.0
```

## 🔧 配置

### 端口修改

默认端口: 8501

修改端口:
```bash
streamlit run src/dashboard/app.py --server.port 8080
```

### 缓存时间

在 `app.py` 中修改:
```python
@st.cache_data(ttl=300)  # 300秒 = 5分钟
```

## 📸 截图

### 市场概览
![Market Overview](../../docs/screenshots/overview.png)

### 综合信号
![Trading Signals](../../docs/screenshots/signals.png)

## 🐛 故障排除

### 1. 数据文件未找到
**错误**: `FileNotFoundError: data/processed/capital_flow_analysis.csv`

**解决**: 先运行所有分析脚本
```bash
python src/analysis/capital_flow_analyzer.py
```

### 2. 端口被占用
**错误**: `OSError: [Errno 48] Address already in use`

**解决**: 使用不同端口
```bash
streamlit run src/dashboard/app.py --server.port 8502
```

### 3. 依赖缺失
**错误**: `ModuleNotFoundError: No module named 'streamlit'`

**解决**: 安装依赖
```bash
pip install -r requirements.txt
```

## 💡 使用技巧

### 1. 自动刷新
点击右上角 "⋮" → "Rerun" 或按 `R` 键

### 2. 全屏模式
点击图表右上角的放大图标

### 3. 导出数据
在图表上悬停 → 点击相机图标保存图片

### 4. 侧边栏
点击左上角 ">" 展开/收起侧边栏

## 🎯 后续功能

- [ ] 实时数据更新（WebSocket）
- [ ] 用户自定义指标
- [ ] 警报通知系统
- [ ] 历史回测可视化
- [ ] 多币种支持
- [ ] 移动端优化

## 📝 更新日志

### v1.0.0 (2025-10-25)
- ✅ 首次发布
- ✅ 6个完整页面
- ✅ 30+交互式图表
- ✅ 综合信号系统

## 📞 支持

遇到问题？请提交Issue或联系开发团队。

---

**Powered by Streamlit & Plotly**  
**Bitcoin Research Agent Team © 2025**

