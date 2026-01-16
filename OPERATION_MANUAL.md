# MCNP6 AI Assistant 操作手册

## 1. 软件概述

MCNP6 AI Assistant是一款整合AI和MCNP6的Windows桌面应用程序，用于分析、诊断和补全MCNP6输入文件，并能调用本地MCNP6进行运行和保存输出文件。

### 主要功能
- ✅ MCNP6输入文件编辑器（语法高亮、自动保存）
- ✅ AI分析诊断（语法检查、错误定位、补全建议）
- ✅ MCNP6运行管理（本地执行、实时监控、结果保存）
- ✅ 输出文件查看（结果解析、关键信息提取）
- ✅ 多模式AI支持（在线API和本地AI）
- ✅ 图形化配置界面（AI和MCNP6设置）

## 2. 系统要求与安装

### 系统要求
- Windows 10/11
- Python 3.8+
- MCNP6已安装并配置

### 安装步骤
1. 克隆或下载项目
2. 安装Python依赖：`pip install -r requirements.txt`
3. 复制 `.env.example` 为 `.env` 并配置
4. 启动程序：`python main.py`

## 3. AI设置详细说明

### 3.1 图形化AI设置界面

通过菜单栏访问AI设置：
1. 点击菜单栏 "设置" → "AI设置"
2. 在弹出的对话框中配置AI参数

### 3.2 AI模式选择

应用支持两种AI模式：

#### 3.2.1 在线AI模式（默认）

使用云端AI服务（如OpenAI、Azure OpenAI等）。

**配置参数：**
- **API密钥**：OpenAI API密钥或其他兼容的API密钥
- **API基础URL**：API服务地址（默认：`https://api.openai.com/v1`）
- **AI模型**：使用的AI模型名称（默认：`gpt-4`）
- **温度**：控制AI输出的随机性（0.0-2.0，默认：0.7）
- **最大令牌数**：控制AI输出的长度（默认：2000）

**配置示例：**
```env
AI_MODE=online
AI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_API_BASE=https://api.openai.com/v1
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
```

#### 3.2.2 本地AI模式

使用本地AI服务（如Ollama）。

**配置参数：**
- **本地端点**：本地AI服务的API地址（默认：`http://localhost:11434/api/generate`）
- **本地模型**：本地AI模型名称（如：`llama2`、`mistral`、`codellama`）
- **温度**：控制AI输出的随机性（0.0-2.0，默认：0.7）
- **最大令牌数**：控制AI输出的长度（默认：2000）

**配置示例：**
```env
AI_MODE=local
AI_LOCAL_ENDPOINT=http://localhost:11434/api/generate
AI_LOCAL_MODEL=llama2
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000
```

### 3.3 Ollama本地AI配置步骤

1. **安装Ollama**：访问 https://ollama.ai 下载并安装
2. **启动Ollama服务**：`ollama serve`
3. **下载模型**：
   ```bash
   ollama pull llama2    # 下载Llama 2模型
   # 或
   ollama pull mistral   # 下载Mistral模型
   ```
4. **在应用中配置**：
   - 选择 "本地AI" 模式
   - 确认端点地址：`http://localhost:11434/api/generate`
   - 设置模型名称（如 `llama2`）
   - 点击 "测试连接" 验证配置
   - 点击 "保存" 应用设置

### 3.4 AI功能使用

#### 3.4.1 AI语法诊断
- **快捷键**：F8
- **功能**：智能检测MCNP6输入文件的语法错误
- **使用方法**：
  1. 编写或打开MCNP6输入文件
  2. 点击菜单栏 "工具" → "AI语法诊断" 或按F8
  3. 等待AI分析完成
  4. 查看编辑器中的高亮标记（红色错误、黄色警告）
  5. 在AI分析结果标签页查看详细报告

#### 3.4.2 AI分析输入文件
- **快捷键**：F5
- **功能**：全面分析输入文件结构、物理合理性等
- **使用方法**：点击菜单栏 "工具" → "AI分析输入文件" 或按F5

#### 3.4.3 AI补全输入文件
- **功能**：根据部分内容智能补全缺失部分
- **使用方法**：点击菜单栏 "工具" → "AI补全输入文件"

#### 3.4.4 AI优化建议
- **功能**：提供计算效率和精度方面的优化建议
- **使用方法**：点击菜单栏 "工具" → "AI优化建议"

### 3.5 AI诊断结果说明

#### 3.5.1 错误标记
- **错误**：红色背景（#5A1D1D）- 必须修正的语法错误
- **警告**：黄色背景（#4A3D00）- 潜在问题或建议改进

#### 3.5.2 诊断报告格式

```json
{
  "has_errors": true/false,
  "errors": [
    {
      "line": 行号,
      "type": "错误类型",
      "message": "错误描述",
      "suggestion": "修正建议"
    }
  ],
  "warnings": [
    {
      "line": 行号,
      "type": "警告类型",
      "message": "警告描述"
    }
  ],
  "summary": "总体诊断总结"
}
```

## 4. MCNP6设置详细说明

### 4.1 图形化MCNP6设置界面

通过菜单栏访问MCNP6设置：
1. 点击菜单栏 "设置" → "MCNP6设置"
2. 在弹出的对话框中配置MCNP6参数

### 4.2 MCNP6执行方式

应用支持两种MCNP6执行方式：

#### 4.2.1 方式一：直接执行MCNP6

如果MCNP6可以直接通过可执行文件运行：

**配置参数：**
- **MCNP6执行路径**：MCNP6可执行文件的完整路径（如：`C:\MCNP6\mcnp6.exe`）
- **MCNP6可执行文件**：留空
- **环境批处理文件**：可选，用于加载环境变量

**配置示例：**
```env
MCNP6_PATH=C:\MCNP6\mcnp6.exe
MCNP6_CMD=
MCNP6_ENV_BAT=
MCNP6_WORKSPACE=./workspace
```

#### 4.2.2 方式二：通过CMD执行MCNP6

如果MCNP6需要通过命令提示符执行（如您当前使用的版本）：

**配置参数：**
- **MCNP6执行路径**：Windows命令提示符的完整路径（通常是：`C:\Windows\System32\cmd.exe`）
- **MCNP6可执行文件**：MCNP6实际可执行文件的完整路径
- **环境批处理文件**：可选，用于加载环境变量（如：`C:\Users\YourName\mcnp_env.bat`）

**配置示例：**
```env
MCNP6_PATH=C:\Windows\System32\cmd.exe
MCNP6_CMD=C:\MCNP6\mcnp6.exe
MCNP6_ENV_BAT=C:\Users\Administer\mcnp_env.bat
MCNP6_WORKSPACE=./workspace
```

### 4.3 环境批处理文件配置

**功能**：用于加载MCNP6运行所需的环境变量（如路径、许可证等）

**设置方法：**
1. 在MCNP6设置界面中点击 "浏览..." 按钮选择批处理文件
2. 或直接输入批处理文件的完整路径

**默认位置：** 如果未指定，应用将使用 `%HOMEDRIVE%%HOMEPATH%\mcnp_env.bat`

### 4.4 工作目录设置

**功能**：指定MCNP6运行时输出文件的保存位置

**配置方法：**
1. 在MCNP6设置界面中点击 "浏览..." 按钮选择目录
2. 或直接输入目录路径

**注意事项：**
- 确保该目录具有读写权限
- 建议使用绝对路径
- 程序会自动创建该目录（如果不存在）

### 4.5 配置验证

**测试MCNP6连接：**
1. 在MCNP6设置界面中配置完成后
2. 点击 "测试MCNP6" 按钮
3. 应用将尝试执行MCNP6并验证配置是否正确
4. 查看测试结果提示

### 4.6 跨电脑使用配置

当在不同电脑上使用应用时：
1. 在每台电脑上启动应用
2. 进入 "MCNP6设置" 界面
3. 配置该电脑上的MCNP6执行路径和环境批处理文件
4. 点击 "保存" 应用设置

**配置文件位置：** 所有配置保存在项目根目录下的 `.env` 文件中

## 5. MCNP6运行管理

### 5.1 运行MCNP6

#### 方式一：通过编辑器
1. 在编辑器中编写或打开MCNP6输入文件
2. 点击菜单栏 "运行" → "运行MCNP6" 或按F6
3. 等待MCNP6启动
4. 在MCNP6输出标签页查看实时运行状态

#### 方式二：通过左侧面板
1. 在左侧控制面板选择或浏览输入文件
2. 点击 "运行" 按钮

### 5.2 停止运行
- **快捷键**：F7
- **功能**：停止正在运行的MCNP6模拟
- **使用方法**：点击菜单栏 "运行" → "停止运行" 或按F7

### 5.3 输出文件管理

#### 5.3.1 输出文件类型
- `*.o`：MCNP6输出文件
- `*.r`：MCNP6运行时文件
- `*.m`：MCNP6结果文件
- `*.w`：MCNP6权重文件

#### 5.3.2 加载输出文件

**注意：** 应用不会自动加载大型输出文件，用户可以选择在运行完成后手动加载。

**加载方法：**
1. 运行完成后，应用会提示是否加载输出文件
2. 点击 "是" 加载输出文件
3. 或通过菜单栏 "文件" → "加载输出文件" 手动加载

## 6. 输入文件编辑器使用

### 6.1 基本操作
- **新建文件**：快捷键 Ctrl+N
- **打开文件**：快捷键 Ctrl+O
- **保存文件**：快捷键 Ctrl+S
- **退出程序**：快捷键 Ctrl+Q

### 6.2 编辑器功能
- ✅ 语法高亮显示
- ✅ 行号显示
- ✅ 自动保存功能
- ✅ 字符数统计
- ✅ 光标位置显示

## 7. 快捷键汇总

| 快捷键 | 功能 |
|--------|------|
| Ctrl+N | 新建文件 |
| Ctrl+O | 打开文件 |
| Ctrl+S | 保存文件 |
| Ctrl+Q | 退出程序 |
| F5 | AI分析输入文件 |
| F6 | 运行MCNP6 |
| F7 | 停止运行 |
| F8 | AI语法诊断 |

## 8. 常见问题与解决方案

### 8.1 AI相关问题

#### Q: AI分析失败
A: 
- 检查AI模式设置是否正确（在线或本地）
- 如果使用在线API：检查API密钥是否正确，网络连接是否正常
- 如果使用本地AI：检查本地AI服务是否已启动，端点地址是否正确

#### Q: 如何使用本地AI（如Ollama）？
A: 
1. 安装Ollama：访问 https://ollama.ai 下载并安装
2. 启动Ollama服务：`ollama serve`
3. 下载模型：`ollama pull llama2`
4. 在应用中配置本地AI参数
5. 点击 "测试连接" 验证

### 8.2 MCNP6相关问题

#### Q: MCNP6运行失败
A: 
- 检查MCNP6路径是否正确
- 工作目录是否有读写权限
- 输入文件格式是否正确
- 环境批处理文件是否正确配置

#### Q: 找不到MCNP6可执行文件
A: 
- 使用绝对路径而不是相对路径
- 确保路径使用正确的分隔符（Windows使用反斜杠`\`）
- 检查文件扩展名是否为`.exe`

#### Q: CMD窗口瞬间关闭
A: 
- 确保使用了正确的执行方式（直接执行或CMD执行）
- 检查环境批处理文件路径是否正确
- 确认MCNP6可执行文件存在

## 9. 技术支持

如有问题或建议，请：
1. 查看应用程序日志文件
2. 检查MCNP6官方文档
3. 联系技术支持

---

**最后更新：** 2026-01-16
**适用版本：** MCNP6 AI Assistant v1.1.0

---

## 附录：配置文件示例

### 完整的 `.env` 配置示例

```env
# MCNP6配置
MCNP6_PATH=C:\Windows\System32\cmd.exe
MCNP6_CMD=C:\MCNP6\mcnp6.exe
MCNP6_ENV_BAT=C:\Users\Administer\mcnp_env.bat
MCNP6_WORKSPACE=E:\MCNP

# AI配置
AI_MODE=online
AI_API_KEY=your_api_key_here
AI_API_BASE=https://api.openai.com/v1
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2000

# 应用配置
DEFAULT_ENCODING=utf-8
AUTO_SAVE_INTERVAL=300
LOG_LEVEL=INFO
```
