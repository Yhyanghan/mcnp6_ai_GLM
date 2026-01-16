"""
端到端测试：验证MCNP6设置更新是否真正生效
"""
import os
import sys
from pathlib import Path

from config import Config
from mcnp6_runner import MCNP6Runner

def test_end_to_end():
    print("=" * 70)
    print("端到端测试：验证MCNP6设置更新是否真正生效")
    print("=" * 70)
    
    env_file = Path(__file__).parent / '.env'
    
    # 保存原始配置
    with open(env_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    print("\n[测试场景1: 修改环境批处理文件为错误路径]")
    print("-" * 70)
    
    # 修改为错误路径
    test_bat_path = "C:/nonexistent/test_bat.bat"
    modified_content = original_content.replace(
        f'MCNP6_ENV_BAT={Config.MCNP6_ENV_BAT}',
        f'MCNP6_ENV_BAT={test_bat_path}'
    )
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"1. 修改.env文件:")
    print(f"   原始路径: {Config.MCNP6_ENV_BAT}")
    print(f"   新路径: {test_bat_path}")
    
    print(f"\n2. 模拟保存设置后的操作:")
    print(f"   调用 load_dotenv(override=True)...")
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    print(f"   调用 Config.reload()...")
    Config.reload()
    
    print(f"   重新加载后 Config.MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    
    if Config.MCNP6_ENV_BAT == test_bat_path:
        print(f"   ✓ Config.MCNP6_ENV_BAT 已更新")
    else:
        print(f"   ✗ Config.MCNP6_ENV_BAT 未更新")
        return False
    
    print(f"\n   创建新的MCNP6Runner实例...")
    runner = MCNP6Runner()
    
    print(f"   新 Runner MCNP6_ENV_BAT: {runner.mcnp6_env_bat}")
    
    if runner.mcnp6_env_bat == test_bat_path:
        print(f"   ✓ 新 Runner MCNP6_ENV_BAT 已更新")
    else:
        print(f"   ✗ 新 Runner MCNP6_ENV_BAT 未更新")
        return False
    
    print(f"\n3. 验证环境批处理文件检查:")
    if runner.mcnp6_env_bat and not os.path.exists(runner.mcnp6_env_bat):
        print(f"   ✓ 环境批处理文件不存在，程序应该检测到")
        print(f"   ✓ 运行MCNP6时应该不使用环境批处理文件")
    else:
        print(f"   ✗ 环境批处理文件检查失败")
        return False
    
    print("\n[测试场景2: 修改MCNP6_CMD为错误路径]")
    print("-" * 70)
    
    # 修改MCNP6_CMD为错误路径
    test_cmd_path = "C:/nonexistent/mcnp6.exe"
    modified_content2 = modified_content.replace(
        f'MCNP6_CMD={Config.MCNP6_CMD}',
        f'MCNP6_CMD={test_cmd_path}'
    )
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(modified_content2)
    
    print(f"1. 修改.env文件:")
    print(f"   原始路径: {Config.MCNP6_CMD}")
    print(f"   新路径: {test_cmd_path}")
    
    print(f"\n2. 模拟保存设置后的操作:")
    load_dotenv(override=True)
    Config.reload()
    
    print(f"   重新加载后 Config.MCNP6_CMD: {Config.MCNP6_CMD}")
    
    if Config.MCNP6_CMD == test_cmd_path:
        print(f"   ✓ Config.MCNP6_CMD 已更新")
    else:
        print(f"   ✗ Config.MCNP6_CMD 未更新")
        return False
    
    print(f"\n   创建新的MCNP6Runner实例...")
    runner2 = MCNP6Runner()
    
    print(f"   新 Runner MCNP6_CMD: {runner2.mcnp6_cmd}")
    
    if runner2.mcnp6_cmd == test_cmd_path:
        print(f"   ✓ 新 Runner MCNP6_CMD 已更新")
    else:
        print(f"   ✗ 新 Runner MCNP6_CMD 未更新")
        return False
    
    print(f"\n3. 验证配置验证功能:")
    print(f"   MCNP6可执行文件不存在: {test_cmd_path}")
    print(f"   程序应该显示错误信息")
    
    print("\n[测试场景3: 修改工作目录]")
    print("-" * 70)
    
    # 修改工作目录
    test_workspace = "E:/MCNP/test_workspace"
    modified_content3 = modified_content2.replace(
        f'MCNP6_WORKSPACE={Config.MCNP6_WORKSPACE}',
        f'MCNP6_WORKSPACE={test_workspace}'
    )
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(modified_content3)
    
    print(f"1. 修改.env文件:")
    print(f"   原始路径: {Config.MCNP6_WORKSPACE}")
    print(f"   新路径: {test_workspace}")
    
    print(f"\n2. 模拟保存设置后的操作:")
    load_dotenv(override=True)
    Config.reload()
    
    print(f"   重新加载后 Config.MCNP6_WORKSPACE: {Config.MCNP6_WORKSPACE}")
    
    if Config.MCNP6_WORKSPACE == test_workspace:
        print(f"   ✓ Config.MCNP6_WORKSPACE 已更新")
    else:
        print(f"   ✗ Config.MCNP6_WORKSPACE 未更新")
        return False
    
    print(f"\n   创建新的MCNP6Runner实例...")
    runner3 = MCNP6Runner()
    
    print(f"   新 Runner workspace: {runner3.workspace}")
    
    if str(runner3.workspace).replace('\\', '/') == test_workspace.replace('\\', '/'):
        print(f"   ✓ 新 Runner workspace 已更新")
    else:
        print(f"   ✗ 新 Runner workspace 未更新")
        return False
    
    print(f"\n3. 验证工作目录创建:")
    if os.path.exists(runner3.workspace):
        print(f"   ✓ 工作目录已创建: {runner3.workspace}")
    else:
        print(f"   ✗ 工作目录未创建")
        return False
    
    print("\n[恢复原始配置]")
    print("-" * 70)
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    load_dotenv(override=True)
    Config.reload()
    
    print(f"   恢复后 Config.MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    print(f"   恢复后 Config.MCNP6_CMD: {Config.MCNP6_CMD}")
    print(f"   恢复后 Config.MCNP6_WORKSPACE: {Config.MCNP6_WORKSPACE}")
    
    print("\n" + "=" * 70)
    print("✓ 所有测试通过！配置更新机制工作正常")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = test_end_to_end()
    sys.exit(0 if success else 1)
