# MCNP6 AI Assistant

一个整合AI和MCNP6的Windows桌面应用程序，用于分析、诊断和补全MCNP6输入文件，并能调用本地MCNP6进行运行和保存输出文件。

## 功能特性

### 1. MCNP6输入文件编辑器
- 语法高亮显示
- 行号显示
- 自动保存功能
- 支持打开和保存MCNP6输入文件
- 实时状态显示（行号、列号、字符数）

### 2. AI分析诊断
- **输入文件分析**：检查语法错误、结构完整性、物理合理性
- **输入文件补全**：根据部分内容智能补全缺失部分
- **优化建议**：提供计算效率、精度提升、资源利用等方面的优化建议
- **卡片解释**：详细解释MCNP6各种卡片的功能和用法
- **AI语法诊断**：智能检测语法错误并在编辑器中高亮显示
  - 精确的行号定位
  - 错误和警告分类显示
  - 详细的修正建议
  - 视觉化错误标记（红色错误、黄色警告）
  - **一键执行功能**：
    - 跳转到错误行：快速定位到错误位置
    - 应用补全建议：一键将AI补全内容应用到编辑器
    - 应用优化建议：一键将AI优化建议追加到编辑器
    - 智能按钮状态：根据AI功能自动启用/禁用按钮
- **支持在线API和本地AI**：
  - 在线API：支持OpenAI等云端AI服务
  - 本地AI：支持Ollama等本地AI服务
- **图形化配置界面**：通过菜单栏轻松配置AI参数

### 3. MCNP6运行管理
- 调用本地MCNP6进行计算
- 实时显示运行输出
- 支持停止正在运行的模拟
- 自动保存输出文件

### 4. 输出文件查看
- 查看MCNP6运行结果
- 解析并显示关键信息（tally结果、运行时间、粒子数等）

## 系统要求

- Windows 10/11
- Python 3.8+
- MCNP6已安装并配置

## 安装步骤

### 1. 克隆或下载项目

```bash
cd mcnp6_ai_GLM
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并编辑配置：

```bash
copy .env.example .env
```

编辑 `.env` 文件，设置以下参数：

```env
# MCNP6配置
MCNP6_PATH=C:/MCNP6/mcnp6.exe
MCNP6_WORKSPACE=C:/MCNP6/workspace

# AI配置
# AI_MODE: 'online' for cloud API, 'local' for local AI service
AI_MODE=online

# Online AI Settings (for AI_MODE=online)
AI_API_KEY=your_api_key_here
AI_API_BASE=https://api.openai.com/v1
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000

# Local AI Settings (for AI_MODE=local)
# Example: Ollama API endpoint
AI_LOCAL_ENDPOINT=http://localhost:11434/api/generate
AI_LOCAL_MODEL=llama2
```

**重要配置说明：**

**MCNP6配置：**
- `MCNP6_PATH`: MCNP6可执行文件的完整路径
- `MCNP6_WORKSPACE`: MCNP6工作目录，用于存放输出文件

**AI模式配置：**
- `AI_MODE`: 选择AI模式
  - `online`: 使用在线API（如OpenAI）
  - `local`: 使用本地AI服务（如Ollama）

**在线AI配置（AI_MODE=online）：**
- `AI_API_KEY`: OpenAI API密钥或其他兼容的API密钥
- `AI_API_BASE`: API基础URL（如果使用其他AI服务，请修改此项）
- `AI_MODEL`: 使用的AI模型名称（如gpt-4、gpt-3.5-turbo等）

**本地AI配置（AI_MODE=local）：**
- `AI_LOCAL_ENDPOINT`: 本地AI服务的API端点
  - Ollama默认: `http://localhost:11434/api/generate`
- `AI_LOCAL_MODEL`: 本地AI模型名称
  - Ollama示例: `llama2`, `mistral`, `codellama` 等

**通用AI参数：**
- `AI_TEMPERATURE`: AI生成温度（0.0-2.0），越高越随机
- `AI_MAX_TOKENS`: 最大生成令牌数

### 4. 创建工作目录

确保 `MCNP6_WORKSPACE` 指定的目录存在，程序会自动创建。

## 使用方法

### 启动程序

```bash
python main.py
```

### 基本操作

#### 1. 编辑输入文件
- 点击"文件" → "新建"创建新文件
- 点击"文件" → "打开"打开现有文件
- 在编辑器中输入或修改MCNP6输入文件内容
- 点击"文件" → "保存"保存文件

#### 2. AI分析
- 点击"工具" → "AI分析输入文件"或按F5键
- AI将分析输入文件并显示诊断结果
- 查看AI分析结果标签页获取详细报告

#### 3. AI补全
- 输入部分MCNP6输入文件内容
- 点击"工具" → "AI补全输入文件"
- AI将补全缺失的部分并更新编辑器内容

#### 4. AI优化
- 点击"工具" → "AI优化建议"
- AI将提供计算效率和精度方面的优化建议

#### 5. AI语法诊断
- 点击"工具" → "AI语法诊断"或按F8键
- AI将智能检测输入文件的语法错误
- 错误行将在编辑器中高亮显示（红色背景）
- 警告行将在编辑器中标记（黄色背景）
- 查看AI分析结果标签页获取详细的错误信息和修正建议

#### 6. AI和MCNP6设置
- **AI设置**：
  - 点击"设置" → "AI设置"
  - 选择AI模式（在线API或本地AI）
  - 配置相应的参数
  - 点击"测试连接"验证配置
  - 点击"保存"应用设置

- **MCNP6设置**：
  - 点击"设置" → "MCNP6设置"
  - 浏览并选择MCNP6可执行文件
  - 设置工作目录
  - 点击"测试MCNP6"验证配置
  - 点击"保存"应用设置

#### 6. 运行MCNP6
- 在左侧控制面板选择或浏览输入文件
- 点击"运行"按钮或按F6键启动MCNP6
- 查看MCNP6输出标签页实时监控运行状态
- 运行完成后自动加载输出文件

#### 6. 停止运行
- 点击"停止"按钮或按F7键停止正在运行的模拟

## 项目结构

```
mcnp6_ai_GLM/
├── main.py              # 主程序入口
├── main_window.py       # 主窗口UI
├── editor.py            # 输入文件编辑器
├── ai_analyzer.py       # AI分析模块（支持在线和本地AI）
├── mcnp6_runner.py      # MCNP6运行模块
├── settings_dialog.py   # 设置对话框（AI和MCNP6设置）
├── config.py            # 配置管理
├── requirements.txt     # Python依赖
├── .env.example         # 环境变量示例
├── .env                 # 环境变量配置（需自行创建）
└── README.md           # 说明文档
```

## 快捷键

- `Ctrl+N`: 新建文件
- `Ctrl+O`: 打开文件
- `Ctrl+S`: 保存文件
- `Ctrl+Q`: 退出程序
- `F5`: AI分析输入文件
- `F6`: 运行MCNP6
- `F7`: 停止运行
- `F8`: AI语法诊断

## 注意事项

1. **MCNP6路径配置**：确保 `.env` 文件中的 `MCNP6_PATH` 指向正确的MCNP6可执行文件路径

2. **API密钥安全**：不要将 `.env` 文件提交到版本控制系统

3. **工作目录权限**：确保 `MCNP6_WORKSPACE` 指定的目录有读写权限

4. **AI服务配置**：如果使用非OpenAI的AI服务，需要修改 `AI_API_BASE` 和 `AI_MODEL` 参数

5. **输入文件编码**：建议使用UTF-8编码保存MCNP6输入文件

## 常见问题

### Q: 程序启动时提示配置错误
A: 检查 `.env` 文件是否存在，并确保所有必需的配置项都已正确设置。

### Q: MCNP6运行失败
A: 检查MCNP6路径是否正确，工作目录是否有读写权限，输入文件格式是否正确。

### Q: AI分析失败
A: 
- 检查AI模式设置是否正确（在线或本地）
- 如果使用在线API：检查API密钥是否正确，网络连接是否正常
- 如果使用本地AI：检查本地AI服务是否已启动，端点地址是否正确

### Q: 如何使用本地AI（如Ollama）？
A: 
1. 安装Ollama：访问 https://ollama.ai 下载并安装
2. 启动Ollama服务：`ollama serve`
3. 下载模型：`ollama pull llama2`
4. 在应用中：
   - 点击"设置" → "AI设置"
   - 选择"本地AI"模式
   - 确认端点地址为 `http://localhost:11434/api/generate`
   - 设置模型名称（如 `llama2`）
   - 点击"测试连接"验证
   - 点击"保存"应用设置

### Q: 编辑器中文显示乱码
A: 确保输入文件使用UTF-8编码保存。

## 技术支持

如有问题或建议，请联系开发者。

## 许可证

本项目仅供教学和研究使用。

## 更新日志

### v1.1.0 (2024-01-15)
- 新增AI模式选择功能（在线API和本地AI）
- 新增图形化AI设置对话框
- 新增图形化MCNP6设置对话框
- 支持本地AI服务（如Ollama）
- 支持在线AI服务（如OpenAI）
- 在菜单栏添加"设置"菜单
- 改进配置管理和验证

### v1.0.0 (2024-01-15)
- 初始版本发布
- 实现基本的输入文件编辑功能
- 集成AI分析和诊断功能
- 支持MCNP6运行管理
- 添加输出文件查看功能
