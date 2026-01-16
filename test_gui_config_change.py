"""
模拟在GUI中修改配置的过程
"""
import os
from pathlib import Path

from config import Config
from mcnp6_runner import MCNP6Runner

def simulate_gui_config_change():
    print("=" * 70)
    print("模拟在GUI中修改配置的过程")
    print("=" * 70)
    
    env_file = Path(__file__).parent / '.env'
    
    # 保存原始配置
    with open(env_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    print("\n[步骤1] 修改前 - 当前配置:")
    print(f"   MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    print(f"   是否存在: {os.path.exists(Config.MCNP6_ENV_BAT) if Config.MCNP6_ENV_BAT else '未设置'}")
    
    # 创建一个错误的环境批处理文件路径
    wrong_bat_path = "C:/Users/Adminr/wrong_bat.bat"
    
    print(f"\n[步骤2] 模拟在GUI中修改环境批处理文件:")
    print(f"   新路径: {wrong_bat_path}")
    
    # 读取.env文件
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 修改MCNP6_ENV_BAT
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('MCNP6_ENV_BAT='):
            new_lines.append(f'MCNP6_ENV_BAT={wrong_bat_path}\n')
        else:
            new_lines.append(line)
    
    # 写回.env文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"   ✓ .env文件已修改")
    
    # 模拟GUI保存设置后的操作
    print(f"\n[步骤3] 模拟GUI保存设置后的操作:")
    print(f"   调用 load_dotenv(override=True)...")
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    print(f"   调用 Config.reload()...")
    Config.reload()
    
    print(f"   重新加载后 Config.MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    
    if Config.MCNP6_ENV_BAT == wrong_bat_path:
        print(f"   ✓ Config.MCNP6_ENV_BAT 已更新")
    else:
        print(f"   ✗ Config.MCNP6_ENV_BAT 未更新")
        print(f"     期望: {wrong_bat_path}")
        print(f"     实际: {Config.MCNP6_ENV_BAT}")
        return False
    
    # 检查新配置
    print(f"\n[步骤4] 检查新配置:")
    print(f"   MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    print(f"   是否存在: {os.path.exists(Config.MCNP6_ENV_BAT)}")
    
    # 创建新的MCNP6Runner实例（模拟GUI重新创建）
    print(f"\n[步骤5] 创建新的MCNP6Runner实例:")
    runner = MCNP6Runner()
    
    print(f"   Runner.mcnp6_env_bat: {runner.mcnp6_env_bat}")
    print(f"   是否存在: {os.path.exists(runner.mcnp6_env_bat) if runner.mcnp6_env_bat else '未设置'}")
    
    if runner.mcnp6_env_bat == wrong_bat_path:
        print(f"   ✓ Runner.mcnp6_env_bat 已更新")
    else:
        print(f"   ✗ Runner.mcnp6_env_bat 未更新")
        print(f"     期望: {wrong_bat_path}")
        print(f"     实际: {runner.mcnp6_env_bat}")
        return False
    
    # 检查运行时行为
    print(f"\n[步骤6] 检查运行时行为:")
    if runner.mcnp6_env_bat and os.path.exists(runner.mcnp6_env_bat):
        print(f"   ✓ 会使用环境批处理文件")
        print(f"   命令: cmd.exe /C call \"{runner.mcnp6_env_bat}\" && ...")
    else:
        print(f"   ✗ 不会使用环境批处理文件")
        print(f"   命令: cmd.exe /C ...")
        print(f"   ⚠️  环境变量会直接设置")
    
    # 恢复原始配置
    print(f"\n[步骤7] 恢复原始配置:")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    load_dotenv(override=True)
    Config.reload()
    
    print(f"   恢复后 Config.MCNP6_ENV_BAT: {Config.MCNP6_ENV_BAT}")
    
    print("\n" + "=" * 70)
    print("✓ 测试完成！配置更新机制工作正常")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = simulate_gui_config_change()
    print(f"\n结果: {'成功' if success else '失败'}")
