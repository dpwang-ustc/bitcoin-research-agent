# Bitcoin Research Agent - 项目网站

这是 Bitcoin Research Agent 的官方项目展示网站。

## 🚀 在线访问

- **本地**: 直接打开 `index.html` 文件
- **GitHub Pages**: https://dpwang-ustc.github.io/bitcoin-research-agent/
- **Vercel**: 待部署

## 📁 文件结构

```
website/
├── index.html              # 主页
├── css/
│   └── style.css          # 样式表
├── js/
│   └── main.js            # JavaScript 交互
├── images/                # 图片资源
│   └── dashboard-preview.png
└── README.md              # 本文件
```

## 🎨 功能特性

### 1. 响应式设计
- ✅ 桌面端优化
- ✅ 平板适配
- ✅ 移动端友好

### 2. 页面内容
- **首页**: Hero Section + 核心功能展示
- **功能**: 8个核心模块详细介绍
- **Demo**: Dashboard 在线演示 + 报告示例
- **文档**: 完整的使用文档链接
- **关于**: 项目介绍 + 技术栈

### 3. 交互功能
- ✅ 平滑滚动导航
- ✅ 标签页切换
- ✅ 代码复制功能
- ✅ 动画效果
- ✅ 进度条动画
- ✅ 统计数字动画

## 🌐 部署方法

### 方法 1: GitHub Pages（推荐）

#### 自动部署

1. 将 `website/` 目录内容复制到项目根目录或 `docs/` 目录
2. 在 GitHub 仓库设置中启用 GitHub Pages
3. 选择分支和目录（main + /docs 或 main + /root）
4. 保存后自动部署

#### 自定义域名（可选）

1. 在 `website/` 目录创建 `CNAME` 文件
2. 添加你的域名，如: `btc-agent.example.com`
3. 在域名DNS设置中添加 CNAME 记录指向 `username.github.io`

### 方法 2: Vercel

#### 使用 Vercel CLI

```bash
# 安装 Vercel CLI
npm install -g vercel

# 部署
cd website
vercel

# 生产环境部署
vercel --prod
```

#### 使用 Vercel Dashboard

1. 访问 https://vercel.com/
2. 点击 "New Project"
3. 导入 GitHub 仓库
4. 设置根目录为 `website/`
5. 点击 "Deploy"

### 方法 3: Netlify

```bash
# 安装 Netlify CLI
npm install -g netlify-cli

# 部署
cd website
netlify deploy

# 生产环境部署
netlify deploy --prod
```

### 方法 4: 本地预览

#### Python HTTP Server

```bash
cd website
python -m http.server 8000
# 访问 http://localhost:8000
```

#### Node.js HTTP Server

```bash
cd website
npx http-server -p 8000
# 访问 http://localhost:8000
```

#### VS Code Live Server

1. 安装 "Live Server" 扩展
2. 右键 `index.html` 
3. 选择 "Open with Live Server"

## ⚙️ 配置

### 更新内容

编辑 `index.html` 中的以下部分：

#### 1. 项目统计
```html
<div class="stat-number">15</div>  <!-- 已完成任务数 -->
<div class="stat-number">79%</div> <!-- 项目完成度 -->
```

#### 2. GitHub 链接
```html
<a href="https://github.com/username/repo" ...>
```

#### 3. Dashboard URL
```html
<a href="http://localhost:8501" ...>
```

### 添加图片

1. 将图片放入 `images/` 目录
2. 在 `index.html` 中更新路径：
```html
<img src="images/your-image.png" alt="Description">
```

建议添加的图片：
- `dashboard-preview.png` - Dashboard 截图
- `favicon.ico` - 网站图标
- `logo.png` - 项目 Logo

## 🎨 自定义样式

### 颜色主题

编辑 `css/style.css` 中的 CSS 变量：

```css
:root {
    --primary-color: #f7931a;      /* 主色调 */
    --secondary-color: #2c3e50;    /* 次要色 */
    --accent-color: #3498db;       /* 强调色 */
    /* ... 其他颜色 */
}
```

### 字体

```css
body {
    font-family: 'Your-Font', -apple-system, ...;
}
```

## 🔧 维护

### 更新项目进度

1. 修改 `index.html` 中的统计数字
2. 更新进度条百分比
3. 添加新完成的任务到里程碑

### 添加新功能

1. 在 Features Section 添加新的 `feature-card`
2. 更新文档链接
3. 添加相关的 Demo 示例

## 📊 SEO 优化

### Meta 标签

已包含的 SEO 优化：
- ✅ Description meta tag
- ✅ Keywords meta tag
- ✅ Semantic HTML5 tags
- ✅ Alt text for images

### 添加更多优化

1. **Open Graph 标签** (社交媒体分享):
```html
<meta property="og:title" content="Bitcoin Research Agent">
<meta property="og:description" content="...">
<meta property="og:image" content="...">
```

2. **Twitter Card**:
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="...">
```

3. **Google Analytics**:
```html
<!-- 在 </head> 前添加 GA 代码 -->
```

## 🚨 故障排除

### 样式不生效
- 检查 CSS 文件路径是否正确
- 清除浏览器缓存 (Ctrl + Shift + R)

### JavaScript 不工作
- 打开浏览器控制台查看错误
- 确认 `main.js` 已正确加载

### 图片不显示
- 检查图片路径
- 确认图片文件存在
- 使用占位符图片

### 移动端显示异常
- 检查 viewport meta tag
- 测试响应式断点
- 使用浏览器开发者工具的移动端模式

## 📝 待办事项

- [ ] 添加 Dashboard 实际截图
- [ ] 创建项目 Logo
- [ ] 添加 Favicon
- [ ] 集成 Google Analytics
- [ ] 添加 Cookie 同意提示（如需要）
- [ ] 优化图片加载（lazy loading）
- [ ] 添加暗色模式切换

## 📚 参考资源

- [GitHub Pages 文档](https://docs.github.com/pages)
- [Vercel 文档](https://vercel.com/docs)
- [Netlify 文档](https://docs.netlify.com/)
- [Font Awesome Icons](https://fontawesome.com/icons)

## 🤝 贡献

欢迎提交 PR 来改进网站！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

---

**更新日期**: 2025-10-26  
**版本**: v1.0.0  
**维护者**: Bitcoin Research Agent Team

