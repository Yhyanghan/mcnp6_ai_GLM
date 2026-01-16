"""
测试配置更新是否生效
"""
import os
import sys
from pathlib import Path

from config import Config
from mcnp6_runner import MCNP6Runner

def test_config_reload():
    print("=" * 60)
    print("测试配置更新是否生效")
    print("=" * 60)
    
    print("\n[1] 当前配置:")
    print(f"   MCNP6_PATH: {Config.MCNP6_PATH}")
    print(f"   MCNP6_CMD: {Config.MCNP6_CMD}")
    print(f"   MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    print(f"   MCNP6_WORKSPACE: {Config.MCNP6_WORKSPACE}")
    
    print("\n[2] 创建MCNP6Runner实例:")
    runner = MCNP6Runner()
    print(f"   Runner MCNP6_PATH: {runner.mcnp6_path}")
    print(f"   Runner MCNP6_CMD: {runner.mcnp6_cmd}")
    print(f"   Runner MCNP6_ENV_BAT: {runner.mcnp6_env_bat}")
    print(f"   Runner workspace: {runner.workspace}")
    
    print("\n[3] 验证配置一致性:")
    if runner.mcnp6_path == Config.MCNP6_PATH:
        print(f"   ✓ MCNP6_PATH 一致")
    else:
        print(f"   ✗ MCNP6_PATH 不一致")
        print(f"     Config: {Config.MCNP6_PATH}")
        print(f"     Runner: {runner.mcnp6_path}")
    
    if runner.mcnp6_cmd == Config.MCNP6_CMD:
        print(f"   ✓ MCNP6_CMD 一致")
    else:
        print(f"   ✗ MCNP6_CMD 不一致")
        print(f"     Config: {Config.MCNP6_CMD}")
        print(f"     Runner: {runner.mcnp6_cmd}")
    
    if runner.mcnp6_env_bat == Config.MCNP6_ENV_BAT:
        print(f"   ✓ MCNP6_ENV_BAT 一致")
    else:
        print(f"   ✗ MCNP6_ENV_BAT 不一致")
        print(f"     Config: {Config.MCNP6_ENV_BAT}")
        print(f"     Runner: {runner.mcnp6_env_bat}")
    
    if str(runner.workspace) == Config.MCNP6_WORKSPACE:
        print(f"   ✓ MCNP6_WORKSPACE 一致")
    else:
        print(f"   ✗ MCNP6_WORKSPACE 不一致")
        print(f"     Config: {Config.MCNP6_WORKSPACE}")
        print(f"     Runner: {runner.workspace}")
    
    print("\n[4] 模拟修改.env文件:")
    env_file = Path(__file__).parent / '.env'
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 修改MCNP6_ENV_BAT为错误路径
    test_bat_path = "C:/nonexistent/test_bat.bat"
    modified_content = content.replace(
        f'MCNP6_ENV_BAT={Config.MCNP6_ENV_BAT}',
        f'MCNP6_ENV_BAT={test_bat_path}'
    )
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"   修改前: MCNP6_ENV_BAT={Config.MCNP6_ENV_BAT}")
    print(f"   修改后: MCNP6_ENV_BAT={test_bat_path}")
    
    print("\n[5] 重新加载配置:")
    Config.reload()
    print(f"   重新加载后 Config.MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    
    if Config.MCNP6_ENV_BAT == test_bat_path:
        print(f"   ✓ Config.MCNP6_ENV_BAT 已更新")
    else:
        print(f"   ✗ Config.MCNP6_ENV_BAT 未更新")
    
    print("\n[6] 创建新的MCNP6Runner实例:")
    runner2 = MCNP6Runner()
    print(f"   新 Runner MCNP6_ENV_BAT: {runner2.mcnp6_env_bat}")
    
    if runner2.mcnp6_env_bat == test_bat_path:
        print(f"   ✓ 新 Runner MCNP6_ENV_BAT 已更新")
    else:
        print(f"   ✗ 新 Runner MCNP6_ENV_BAT 未更新")
    
    print("\n[7] 验证环境批处理文件检查:")
    if runner2.mcnp6_env_bat and not os.path.exists(runner2.mcnp6_env_bat):
        print(f"   ✓ 环境批处理文件不存在，程序应该检测到")
    else:
        print(f"   ✗ 环境批处理文件检查失败")
    
    print("\n[8] 恢复原始配置:")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    Config.reload()
    print(f"   恢复后 Config.MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_config_reload()
