# MCNP6配置指南

本指南详细说明如何正确配置MCNP6路径和执行方式，确保MCNP6 AI Assistant能够顺利调用MCNP6进行模拟计算。

## 配置概述

MCNP6 AI Assistant支持两种MCNP6执行方式：
1. **直接执行方式**：直接调用MCNP6可执行文件
2. **CMD执行方式**：通过Windows命令提示符(cmd.exe)调用MCNP6

根据您的MCNP6安装方式和版本，选择合适的配置方式。

## 环境变量配置

在项目根目录下的`.env`文件中配置以下环境变量：

### 方式一：直接执行MCNP6

如果您的MCNP6可以直接通过可执行文件运行，使用以下配置：

```env
MCNP6_PATH=C:\MCNP6\mcnp6.exe
MCNP6_CMD=
MCNP6_WORKSPACE=./workspace
```

**配置说明：**
- `MCNP6_PATH`：MCNP6可执行文件的完整路径
- `MCNP6_CMD`：留空（不使用cmd执行）
- `MCNP6_WORKSPACE`：MCNP6输出文件的工作目录

### 方式二：通过CMD执行MCNP6

如果您的MCNP6需要通过命令提示符执行（如您的版本），使用以下配置：

```env
MCNP6_PATH=C:\Windows\System32\cmd.exe
MCNP6_CMD=C:\MCNP6\mcnp6.exe
MCNP6_WORKSPACE=./workspace
```

**配置说明：**
- `MCNP6_PATH`：Windows命令提示符的完整路径（通常是`C:\Windows\System32\cmd.exe`）
- `MCNP6_CMD`：MCNP6可执行文件的完整路径
- `MCNP6_WORKSPACE`：MCNP6输出文件的工作目录

## 常见配置场景

### 场景1：MCNP6安装在系统目录

```env
MCNP6_PATH=C:\Program Files\MCNP6\mcnp6.exe
MCNP6_CMD=
MCNP6_WORKSPACE=./workspace
```

### 场景2：MCNP6安装在用户目录

```env
MCNP6_PATH=C:\Users\YourName\MCNP6\mcnp6.exe
MCNP6_CMD=
MCNP6_WORKSPACE=./workspace
```

### 场景3：MCNP6通过批处理文件启动

```env
MCNP6_PATH=C:\Windows\System32\cmd.exe
MCNP6_CMD=C:\MCNP6\run_mcnp6.bat
MCNP6_WORKSPACE=./workspace
```

### 场景4：MCNP6在PATH环境变量中

```env
MCNP6_PATH=mcnp6.exe
MCNP6_CMD=
MCNP6_WORKSPACE=./workspace
```

## 配置验证

配置完成后，可以通过以下方式验证配置是否正确：

### 1. 检查文件是否存在

确保配置的路径指向的文件确实存在：
- 直接执行方式：检查`MCNP6_PATH`指向的mcnp6.exe是否存在
- CMD执行方式：检查`MCNP6_PATH`指向的cmd.exe和`MCNP6_CMD`指向的mcnp6.exe是否存在

### 2. 测试MCNP6执行

在命令提示符中手动测试MCNP6是否可以正常运行：

**直接执行方式：**
```bash
cd C:\MCNP6
mcnp6.exe i=test.inp o=test.out r=test.r
```

**CMD执行方式：**
```bash
cmd /c mcnp6.exe i=test.inp o=test.out r=test.r
```

### 3. 应用程序内验证

启动MCNP6 AI Assistant后：
1. 打开"设置" → "MCNP6设置"
2. 检查显示的MCNP6路径是否正确
3. 如果有配置错误，应用会显示警告信息

## 故障排除

### 问题1：程序运行MCNP6时自动退出

**可能原因：**
- MCNP6路径配置不正确
- MCNP6可执行文件不存在
- 执行方式选择错误

**解决方案：**
1. 检查`.env`文件中的`MCNP6_PATH`配置
2. 确认MCNP6可执行文件确实存在于指定路径
3. 如果MCNP6需要通过cmd.exe执行，确保`MCNP6_PATH`指向cmd.exe，`MCNP6_CMD`指向mcnp6.exe

### 问题2：找不到MCNP6可执行文件

**可能原因：**
- 路径拼写错误
- 文件扩展名不正确
- 路径中包含特殊字符

**解决方案：**
1. 使用绝对路径而不是相对路径
2. 确保路径使用正确的分隔符（Windows使用反斜杠`\`）
3. 检查文件扩展名是否为`.exe`
4. 避免路径中包含空格或特殊字符，如果必须包含，使用引号

### 问题3：MCNP6运行但没有输出

**可能原因：**
- 工作空间权限问题
- 输出文件路径配置错误
- MCNP6参数传递错误

**解决方案：**
1. 确保`MCNP6_WORKSPACE`目录存在且有写入权限
2. 检查MCNP6的输入文件格式是否正确
3. 查看应用程序日志获取详细错误信息

### 问题4：编码问题导致输出乱码

**可能原因：**
- MCNP6输出文件编码与系统默认编码不匹配

**解决方案：**
在`.env`文件中设置正确的编码：
```env
DEFAULT_ENCODING=gbk
# 或
DEFAULT_ENCODING=utf-8
```

## 高级配置

### 自定义MCNP6参数

如果需要传递额外的MCNP6参数，可以修改[mcnp6_runner.py](mcnp6_runner.py)中的命令构造部分：

```python
# 添加额外的MCNP6参数
full_cmd = [self.mcnp6_path, f"i={input_path}", f"o={output_file}", f"r={runtpe_file}", "tasks=4"]
```

### 多版本MCNP6支持

如果需要支持多个MCNP6版本，可以：
1. 创建多个配置文件（如`.env.v1`, `.env.v2`）
2. 在应用程序中添加版本选择功能
3. 根据选择的版本加载不同的配置

## 工作空间管理

### 工作空间结构

MCNP6运行时会在工作空间目录下生成以下文件：
- `*.o`：MCNP6输出文件
- `*.r`：MCNP6运行时文件
- `*.m`：MCNP6结果文件
- `*.w`：MCNP6权重文件

### 工作空间清理

定期清理工作空间可以节省磁盘空间：
```python
import os
import glob

workspace = "./workspace"
for file in glob.glob(os.path.join(workspace, "*")):
    if file.endswith(('.o', '.r', '.m', '.w')):
        os.remove(file)
```

## 性能优化

### 并行计算

如果MCNP6支持并行计算，可以配置使用多个CPU核心：
```env
MCNP6_TASKS=4
```

### 内存限制

根据系统内存情况，可以设置MCNP6的内存使用限制：
```env
MCNP6_MEMORY=4GB
```

## 安全注意事项

1. **路径安全**：确保MCNP6路径指向可信的MCNP6安装
2. **文件权限**：工作空间目录应该有适当的读写权限
3. **环境变量**：不要在`.env`文件中存储敏感信息
4. **日志记录**：定期检查应用程序日志，监控MCNP6执行情况

## 联系支持

如果遇到配置问题无法解决，请：
1. 检查应用程序日志文件
2. 查看MCNP6官方文档
3. 联系MCNP6技术支持

## 附录：完整配置示例

### 示例1：标准配置（直接执行）

```env
# MCNP6配置
MCNP6_PATH=C:\MCNP6\mcnp6.exe
MCNP6_CMD=
MCNP6_WORKSPACE=./workspace

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

### 示例2：CMD执行配置

```env
# MCNP6配置
MCNP6_PATH=C:\Windows\System32\cmd.exe
MCNP6_CMD=C:\MCNP6\mcnp6.exe
MCNP6_WORKSPACE=./workspace

# AI配置
AI_MODE=local
AI_LOCAL_ENDPOINT=http://localhost:11434/api/generate
AI_LOCAL_MODEL=llama2

# 应用配置
DEFAULT_ENCODING=gbk
AUTO_SAVE_INTERVAL=300
LOG_LEVEL=DEBUG
```

---

**最后更新：** 2026-01-15
**适用版本：** MCNP6 AI Assistant v1.0
