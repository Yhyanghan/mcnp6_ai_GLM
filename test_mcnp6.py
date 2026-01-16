import subprocess
import os
from pathlib import Path

# 测试MCNP6的直接调用
mcnp6_exe = r"D:\BaiduNetdiskDownload\MCNP6.1(可执行程序包)\MCNP6\MCNP\MCNP\MCNP_CODE\bin\mcnp6.exe"
test_input = r"test.inp"
test_output = r"test.out"
test_runtpe = r"test.r"

# 设置环境变量
env = os.environ.copy()
env['MCNPPATH'] = r"D:\BaiduNetdiskDownload\MCNP6.1(可执行程序包)\MCNP6\MCNP\MCNP\MCNP_CODE\bin"
env['DATAPATH'] = r"D:\BaiduNetdiskDownload\MCNP6.1(可执行程序包)\MCNP6\MCNP\MCNP\MCNP_DATA"
env['DISPLAY'] = ':0.0'

# 测试不同的命令格式
commands = [
    f'"{mcnp6_exe}" i="{test_input}" o="{test_output}" r="{test_runtpe}"',
    f'{mcnp6_exe} i="{test_input}" o="{test_output}" r="{test_runtpe}"',
    f'"{mcnp6_exe}" i={test_input} o={test_output} r={test_runtpe}',
    f'{mcnp6_exe} i={test_input} o={test_output} r={test_runtpe}',
]

for i, cmd in enumerate(commands):
    print(f"\n=== 测试命令 {i+1}: {cmd} ===")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=r"E:\MCNP",
            shell=True
        )
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout[:200]}")
        print(f"标准错误: {result.stderr[:200]}")
    except Exception as e:
        print(f"错误: {e}")

# 测试通过cmd.exe调用
cmd_exe = r"C:\Windows\System32\cmd.exe"
cmd_command = f'{cmd_exe} /c "{commands[0]}"'
print(f"\n=== 测试CMD调用: {cmd_command} ===")
try:
    result = subprocess.run(
        cmd_command,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
        cwd=r"E:\MCNP",
        shell=True
    )
    print(f"返回码: {result.returncode}")
    print(f"标准输出: {result.stdout[:200]}")
    print(f"标准错误: {result.stderr[:200]}")
except Exception as e:
    print(f"错误: {e}")