import subprocess
import os
import logging
import psutil
from typing import Dict, Optional, Callable
from pathlib import Path
from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class MCNP6Runner:
    def __init__(self):
        self.mcnp6_path = Config.MCNP6_PATH
        self.mcnp6_cmd = Config.MCNP6_CMD if hasattr(Config, 'MCNP6_CMD') else None
        self.workspace = Path(Config.MCNP6_WORKSPACE)
        self.current_process: Optional[subprocess.Popen] = None
        self._ensure_workspace()
        self._setup_mcnp6_environment()
    
    def _ensure_workspace(self):
        os.makedirs(self.workspace, exist_ok=True)
        logger.info(f"工作空间: {self.workspace}")
    
    def _setup_mcnp6_environment(self):
        if self.mcnp6_cmd:
            mcnp6_dir = str(Path(self.mcnp6_cmd).parent)
            os.environ['MCNPPATH'] = mcnp6_dir
            if mcnp6_dir not in os.environ['PATH']:
                os.environ['PATH'] = mcnp6_dir + os.pathsep + os.environ['PATH']
            logger.info(f"MCNP6环境变量已设置: MCNPPATH={mcnp6_dir}")
            
            datapath = str(Path(mcnp6_dir).parent.parent.joinpath("MCNP_DATA"))
            if os.path.exists(datapath):
                os.environ['DATAPATH'] = datapath
                logger.info(f"MCNP6数据路径已设置: DATAPATH={datapath}")
            else:
                logger.warning(f"MCNP6数据路径不存在: {datapath}")
            
            os.environ['DISPLAY'] = ':0.0'
            logger.info("DISPLAY环境变量已设置")
    
    def run_simulation(self, input_file: str, output_callback: Optional[Callable] = None) -> Dict:
        input_path = Path(input_file)
        if not input_path.exists():
            return {"success": False, "error": f"输入文件不存在: {input_file}"}
        
        input_filename = input_path.name
        input_stem = input_path.stem
        
        output_file = self.workspace / f"{input_stem}.o"
        runtpe_file = self.workspace / f"{input_stem}.r"
        mctal_file = self.workspace / f"{input_stem}.m"
        
        try:
            env = os.environ.copy()
            
            if 'cmd.exe' in self.mcnp6_path.lower():
                mcnp6_executable = self.mcnp6_cmd if self.mcnp6_cmd else 'mcnp6.exe'
                
                mcnp6_dir = str(Path(mcnp6_executable).parent)
                logger.info(f"MCNP6目录: {mcnp6_dir}")
                logger.info(f"MCNP6可执行文件: {mcnp6_executable}")
                
                env['MCNPPATH'] = mcnp6_dir
                env['PATH'] = mcnp6_dir + os.pathsep + env['PATH']
                
                datapath = str(Path(mcnp6_dir).parent.parent.joinpath("MCNP_DATA"))
                logger.info(f"计算的数据路径: {datapath}")
                if os.path.exists(datapath):
                    env['DATAPATH'] = datapath
                    logger.info(f"设置数据路径: {datapath}")
                else:
                    logger.warning(f"数据路径不存在: {datapath}")
                
                env['DISPLAY'] = ':0.0'
                
                input_filename = input_path.name
                input_path_str = str(input_path)
                output_file_str = str(output_file)
                runtpe_file_str = str(runtpe_file)
                
                # 完全复制用户的快捷方式行为
                # 1. 使用用户的快捷方式配置：cmd.exe /K + 环境变量 + 起始位置
                # 先扩展环境变量
                # 优先使用用户配置的环境批处理文件，如果没有则使用默认位置
                if hasattr(Config, 'MCNP6_ENV_BAT') and Config.MCNP6_ENV_BAT:
                    env_bat_path = Config.MCNP6_ENV_BAT
                else:
                    # 使用默认位置：用户主目录下的mcnp_env.bat
                    env_bat_path = os.path.expandvars(r"%HOMEDRIVE%%HOMEPATH%\mcnp_env.bat")
                
                # 2. 创建最终的命令：先执行环境变量，然后切换到工作目录，然后执行MCNP6
                # 添加output和runtpe文件参数，保持窗口打开
                command_line = f'cd /d "{self.workspace}" && "{mcnp6_executable}" i="{input_filename}" o="{output_file}" r="{runtpe_file}" && pause'
                
                # 3. 使用正确的cmd.exe路径格式
                cmd_path = r"C:\Windows\System32\cmd.exe"
                
                logger.info(f"通过CMD启动MCNP6: {cmd_path} /K call '{env_bat_path}' && {command_line}")
                logger.info(f"环境批处理文件: {env_bat_path}")
                logger.info(f"工作目录: {self.workspace}")
                logger.info(f"输入文件: {input_filename}")
                logger.info(f"完整输入路径: {input_path_str}")
                
                # 4. 使用shell=True直接执行命令
                full_cmd = f'{cmd_path} /K call "{env_bat_path}" && {command_line}'
                cwd = r"E:\MCNP"
                use_shell = True
            else:
                full_cmd = [self.mcnp6_path, f"i={input_path}", f"o={output_file}", f"r={runtpe_file}"]
                logger.info(f"直接启动MCNP6: {' '.join(full_cmd)}")
                use_shell = False
                # 设置工作目录
                cwd = str(self.workspace)
            
            self.current_process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                cwd=cwd,
                shell=use_shell,
                env=env
            )
            
            output_lines = []
            while True:
                line = self.current_process.stdout.readline()
                if not line and self.current_process.poll() is not None:
                    break
                if line:
                    output_lines.append(line)
                    if output_callback:
                        output_callback(line)
            
            return_code = self.current_process.poll()
            
            if return_code == 0:
                logger.info("MCNP6运行成功")
                result = {
                    "success": True,
                    "output_file": str(output_file),
                    "runtpe_file": str(runtpe_file),
                    "mctal_file": str(mctal_file) if mctal_file.exists() else None,
                    "output": ''.join(output_lines)
                }
            else:
                stderr = ''.join(output_lines)
                logger.error(f"MCNP6运行失败，返回码: {return_code}")
                logger.error(f"错误输出: {stderr[:500]}")
                result = {
                    "success": False,
                    "error": f"MCNP6运行失败，返回码: {return_code}",
                    "stderr": stderr,
                    "output": ''.join(output_lines)
                }
            
            self.current_process = None
            return result
            
        except Exception as e:
            logger.error(f"运行MCNP6时发生错误: {str(e)}", exc_info=True)
            self.current_process = None
            return {"success": False, "error": str(e)}
    
    def stop_simulation(self) -> Dict:
        if self.current_process is None:
            return {"success": False, "error": "没有正在运行的模拟"}
        
        try:
            process = psutil.Process(self.current_process.pid)
            for child in process.children(recursive=True):
                child.kill()
            process.kill()
            
            self.current_process.wait()
            self.current_process = None
            logger.info("MCNP6模拟已停止")
            return {"success": True, "message": "模拟已停止"}
            
        except Exception as e:
            logger.error(f"停止模拟时发生错误: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def is_running(self) -> bool:
        return self.current_process is not None and self.current_process.poll() is None
    
    def get_output_file(self, input_filename: str) -> Optional[str]:
        input_stem = Path(input_filename).stem
        output_file = self.workspace / f"{input_stem}.o"
        return str(output_file) if output_file.exists() else None
    
    def parse_output_file(self, output_file: str) -> Dict:
        if not os.path.exists(output_file):
            return {"success": False, "error": "输出文件不存在"}
        
        try:
            with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            results = {
                "success": True,
                "content": content,
                "tallies": self._extract_tallies(content),
                "runtime": self._extract_runtime(content),
                "particles": self._extract_particles(content),
                "errors": self._extract_errors(content)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"解析输出文件时发生错误: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _extract_tallies(self, content: str) -> list:
        tallies = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'tally' in line.lower() and 'results' in line.lower():
                tallies.append({
                    "line": i + 1,
                    "content": line
                })
        return tallies
    
    def _extract_runtime(self, content: str) -> Optional[float]:
        import re
        match = re.search(r'total cpu time[^\d]*([\d.]+)', content, re.IGNORECASE)
        return float(match.group(1)) if match else None
    
    def _extract_particles(self, content: str) -> Optional[int]:
        import re
        match = re.search(r'number of histories[^\d]*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _extract_errors(self, content: str) -> list:
        errors = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'error' in line.lower() or 'fatal' in line.lower():
                errors.append({
                    "line": i + 1,
                    "content": line.strip()
                })
        return errors
    
    def validate_input_file(self, input_file: str) -> Dict:
        input_path = Path(input_file)
        if not input_path.exists():
            return {"valid": False, "errors": ["文件不存在"]}
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            errors = []
            warnings = []
            
            lines = content.split('\n')
            
            has_cell_card = any(line.strip().startswith('c ') for line in lines)
            has_surface_card = any(line.strip().startswith('s ') for line in lines)
            has_material_card = any(line.strip().startswith('m ') for line in lines)
            has_source_card = any('sdef' in line.lower() for line in lines)
            
            if not has_cell_card:
                errors.append("缺少单元格卡片（Cell Cards）")
            if not has_surface_card:
                errors.append("缺少表面卡片（Surface Cards）")
            if not has_material_card:
                errors.append("缺少材料卡片（Material Cards）")
            if not has_source_card:
                warnings.append("未找到源定义（SDEF）")
            
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('$'):
                    continue
                if line.strip() and not line.strip()[0].isalpha():
                    warnings.append(f"第{i}行: 可能的格式问题")
            
            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
            return result
            
        except Exception as e:
            logger.error(f"验证输入文件时发生错误: {str(e)}")
            return {"valid": False, "errors": [str(e)]}
