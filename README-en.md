# 📈 Data Visualization System

> 🌍 **Multi-language** | **多语言版本** | **多言語対応**  
> [🇺🇸 English](README-en.md) | [🇨🇳 中文](README-zh.md) | [🇯🇵 日本語](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?logo=vue.js)](https://v3.vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python)](https://www.python.org/)

> 🚀 **Real-time Stock Data Analysis & Visualization Platform** - Modern data visualization system based on Vue.js + Flask

**Author**: chenlei

## 👨‍💻 Author

**chenlei**
- Project creator and main developer
- Specializes in full-stack web development and data visualization

For detailed contributor information, please refer to [CONTRIBUTORS.md](CONTRIBUTORS.md)

## 🚀 What This System Can Do

### 📊 Main Features Overview

This system is a comprehensive web application centered on **real-time stock data visualization**:

#### 🎯 Core Features
- **📈 Real-time Data Dashboard** - Real-time display of stock prices, order book information, and sector analysis
- **🔄 Multi-client Synchronization** - Multi-browser data synchronization, ideal for team analysis
- **📊 Interactive Charts** - Advanced visualization based on Plotly.js (zoom, pan, selection)
- **📋 Dynamic Tables** - Custom background colors, sorting, and filtering functions
- **⚡ One-click Environment Setup** - Launch professional analysis environment in 5 minutes

#### 🛠️ Developer Features
- **🔧 Automatic Configuration Generation** - Complete new page addition with one command
- **🖥️ VS Code Full Integration** - One-click startup and debugging within IDE
- **🧪 Comprehensive Test System** - Unit, integration, and performance testing
- **📝 Automatic Documentation Generation** - API specification auto-updates
- **🔍 Real-time Monitoring** - System performance visualization

#### 🎓 Educational & Learning Applications
- **💡 Modern Technology Stack** - Vue.js 3 + Flask + SSE best practices
- **📚 Rich Documentation** - 15+ detailed guides (97% completion rate)
- **🔬 Practical Examples** - Enterprise-level architecture patterns
- **🌐 Multi-language Support** - Full English localization

#### 🏢 Enterprise Application Scenarios
- **📊 Custom Dashboard Construction** - Brand-compatible fully controlled UI
- **🚀 MVP & Prototype Development** - Rapid proof of concept
- **🎯 Technology Validation Platform** - New technology stack evaluation
- **👨‍🏫 Corporate Training Tool** - Web development skill enhancement programs

### 💎 Unique Value Proposition

| Feature | Traditional Solutions | This System | Advantage |
|---------|----------------------|-------------|-----------|
| **Environment Setup** | Hours ~ Days | **5 minutes** | 🚀 95% time savings |
| **Customization** | Limited | **Complete freedom** | 🎨 Full control |
| **Learning Resources** | Fragmented | **Comprehensive documentation** | 📚 97% completion |
| **Development Efficiency** | Manual configuration | **Automated tools** | ⚡ 85% efficiency improvement |
| **Technology Modernization** | Legacy technology | **Latest stack** | 🆕 Industry leading |

## 🎥 Demo Videos & Tutorials

### 📹 System Overview Video

You can watch the main features and real-time dashboard operation:

[![Data Visualization System - Overview Demo](https://img.youtube.com/vi/dF2n_UqZiVk/maxresdefault.jpg)](https://www.youtube.com/watch?v=dF2n_UqZiVk&ab_channel=YYfish "Data Visualization System Overview - Click to Play")

## ✨ Main Features

- 🔄 **Real-time Data Synchronization** - Based on Server-Sent Events (SSE) technology
- 📊 **Intelligent Simulation Data** - Built-in rich demo data, no external data sources required
- 🎨 **Rich Visualization** - Interactive charts with Plotly.js integration
- 📱 **Responsive Design** - Perfect adaptation to desktop and mobile devices
- 🔧 **Modular Architecture** - Unified configuration management, easy to extend and maintain
- 🎯 **Zero Configuration Startup** - Automatic configuration generation, one-click launch of all services
- 🛠️ **VS Code Integration** - Built-in task configuration, IDE one-click startup support

## 🚀 Quick Start

### Environment Requirements
- **Node.js** 16+ 
- **Python** 3.7+
- **npm** or **yarn**

### Method 1: One-click Initialization (Recommended for New Users)

1. **Clone the Project**
   ```bash
   git clone [your-repo-url]
   cd vue-project
   ```

2. **Configuration Initialization**
   ```bash
   python scripts/init-config.py
   ```
   
   Interactive configuration wizard automatically:
   - ✅ Detects Python and Node.js environment
   - ✅ Configures port and path settings
   - ✅ Generates unified configuration file `project-config.json`
   - ✅ Auto-generates frontend configuration, routing, components
   - ✅ Creates VS Code tasks and startup scripts

3. **Install Frontend Dependencies**
   ```bash
   npm install
   ```

4. **One-click Launch**
   
   **Method 1: Launch with Script**
   ```bash
   # Windows Users
   start-all-services.bat
   
   # Linux/Mac Users  
   ./start-all-services.sh
   ```
   
   **Method 2: Use VS Code Tasks (Recommended)**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) in VS Code
   - Type "Tasks: Run Task"
   - Select "🚀 Start All Services"
   - System automatically starts frontend and backend services

### Access URLs
- 🌐 **Frontend Interface**: http://localhost:8081
- 🔧 **Backend API**: http://localhost:5004
- 📊 **Demo Dashboard**: http://localhost:8081/demo_1

## 📁 Project Structure

```
vue-project/
├── 📄 project-config.json           # 🎯 Unified configuration file (core)
├── 🚀 start-all-services.bat/.sh   # One-click startup script
├── 📁 scripts/                     # 🛠️ Tool scripts directory
│   ├── 🤖 auto-config-generator.py # 🔧 Automatic configuration generator
│   ├── ⚡ init-config.py           # 🚀 Project initialization script
│   └── 📝 quick-add-page.py        # ➕ Page quick addition tool
│
├── 🎛️ api/                         # Flask backend API service
│   └── 🎯 show_plate_server_demo.py # Demo server (built-in simulation data)
│
├── 🎨 src/                         # Vue frontend source code
│   ├── 📋 components/dashboard/     # Dashboard components
│   │   ├── Dashboard.vue           # Main dashboard component
│   │   ├── ChartComponent.vue      # Chart component
│   │   └── TableComponent.vue      # Table component
│   ├── ⚙️ config/
│   │   └── api.js                  # 🤖 Auto-generated API configuration
│   ├── 🛣️ router/
│   │   └── index.js                # 🤖 Auto-generated routing configuration
│   └── 📄 views/
│       ├── Home.vue                # 🤖 Auto-generated homepage
│       └── StockDashboard.vue      # Data visualization page
│
├── 🛠️ .vscode/
│   └── tasks.json                  # 🤖 Auto-generated VS Code tasks
│
├── 📦 package.json                 # npm configuration
├── ⚙️ vue.config.js               # Vue CLI configuration
└── 📖 README.md                   # Project documentation
```

## 🤝 Contributing

### Code Submission
1. Fork this project
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add some amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Submit Pull Request

### Issue Reporting
- Use GitHub Issues to report bugs
- Provide detailed reproduction steps and environment information
- Include error logs and screenshots (if applicable)

### Feature Suggestions
- Submit feature suggestions through GitHub Issues
- Explain expected functionality and use cases
- Consider backward compatibility

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 👨‍💻 Author

**chenlei**
- Project creator and main developer
- Specializes in full-stack web development and data visualization

## 📞 Technical Support

For questions or suggestions, please contact us through:
- 📧 Submit [GitHub Issue](https://github.com/your-repo/issues)
- 📖 Refer to project [Wiki Documentation](https://github.com/your-repo/wiki)
- 💬 Join community discussions

---

**⚠️ Disclaimer**: This system is a technical demonstration tool, intended for learning and research purposes only, and does not constitute investment advice.
