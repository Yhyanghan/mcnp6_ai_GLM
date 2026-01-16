import openai
from typing import List, Dict, Optional
import logging
import requests
import json
from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class MCNP6AIAnalyzer:
    def __init__(self):
        self.mode = Config.AI_MODE
        self.temperature = Config.AI_TEMPERATURE
        self.max_tokens = Config.AI_MAX_TOKENS
        
        if self.mode == 'online':
            self.client = openai.OpenAI(
                api_key=Config.AI_API_KEY,
                base_url=Config.AI_API_BASE
            )
            self.model = Config.AI_MODEL
        else:
            self.local_endpoint = Config.AI_LOCAL_ENDPOINT
            self.local_model = Config.AI_LOCAL_MODEL
    
    def _call_online_api(self, messages: List[Dict], temperature: float = None, max_tokens: int = None) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"在线API调用失败: {str(e)}")
            raise
    
    def _call_local_api(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        try:
            payload = {
                "model": self.local_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens
                }
            }
            
            response = requests.post(
                self.local_endpoint,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"本地API返回错误: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"本地API调用失败: {str(e)}")
            raise
    
    def _generate_response(self, prompt: str, system_message: str = None, temperature: float = None, max_tokens: int = None) -> str:
        if self.mode == 'online':
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            return self._call_online_api(messages, temperature, max_tokens)
        else:
            full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
            return self._call_local_api(full_prompt, temperature, max_tokens)
    
    def analyze_input_file(self, input_content: str) -> Dict:
        prompt = f"""你是一个MCNP6蒙特卡罗输运代码的专家。请分析以下MCNP6输入文件，并提供详细的诊断报告。

输入文件内容：
```
{input_content}
```

请从以下几个方面进行分析：
1. 语法检查 - 检查是否有语法错误
2. 结构完整性 - 检查必需的卡片是否完整（如单元格、表面、材料、源等）
3. 物理合理性 - 检查物理参数是否合理
4. 潜在问题 - 识别可能导致运行失败或结果不准确的问题
5. 改进建议 - 提供优化建议

请以结构化的JSON格式返回结果，包含以下字段：
- overall_status: "valid", "warning", 或 "error"
- syntax_errors: 数组，包含语法错误列表
- missing_cards: 数组，包含缺失的必需卡片
- physical_issues: 数组，包含物理问题列表
- suggestions: 数组，包含改进建议
- severity: "low", "medium", 或 "high"
- summary: 简要总结"""

        try:
            result = self._generate_response(
                prompt,
                system_message="你是MCNP6代码的专家，擅长分析输入文件并提供专业的诊断建议。",
                temperature=0.5
            )
            
            logger.info(f"AI分析完成，状态: {result[:100]}...")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def complete_input_file(self, partial_content: str, context: str = "") -> Dict:
        prompt = f"""你是一个MCNP6蒙特卡罗输运代码的专家。请根据以下不完整的MCNP6输入文件内容，补全缺失的部分。

不完整的输入文件：
```
{partial_content}
```

上下文信息：
{context}

请补全输入文件，确保：
1. 语法正确
2. 结构完整
3. 物理参数合理
4. 符合MCNP6规范

请直接返回完整的输入文件内容，不要添加额外的解释。"""

        try:
            completed_content = self._generate_response(
                prompt,
                system_message="你是MCNP6代码的专家，擅长补全和优化输入文件。",
                temperature=0.3
            )
            
            logger.info("输入文件补全完成")
            return {"success": True, "content": completed_content}
            
        except Exception as e:
            logger.error(f"输入文件补全失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def explain_card(self, card_name: str) -> Dict:
        prompt = f"""请详细解释MCNP6中的{card_name}卡片，包括：
1. 卡片的功能和用途
2. 语法格式
3. 参数说明
4. 使用示例
5. 常见错误和注意事项

请提供清晰、专业的解释。"""

        try:
            explanation = self._generate_response(
                prompt,
                system_message="你是MCNP6代码的专家，擅长解释各种卡片的功能和用法。",
                temperature=0.5
            )
            
            return {"success": True, "explanation": explanation}
            
        except Exception as e:
            logger.error(f"卡片解释失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def optimize_input_file(self, input_content: str) -> Dict:
        prompt = f"""你是一个MCNP6蒙特卡罗输运代码的专家。请分析以下MCNP6输入文件，并提供优化建议。

输入文件内容：
```
{input_content}
```

请从以下方面提供优化建议：
1. 计算效率 - 如何减少计算时间
2. 精度提升 - 如何提高计算精度
3. 资源利用 - 如何更好地利用计算资源
4. 参数调整 - 建议调整的参数及其原因

请提供具体的优化建议，并说明每个建议的理由。"""

        try:
            optimization = self._generate_response(
                prompt,
                system_message="你是MCNP6代码的专家，擅长优化输入文件以提高计算效率和精度。",
                temperature=0.5
            )
            
            logger.info("优化建议生成完成")
            return {"success": True, "suggestions": optimization}
            
        except Exception as e:
            logger.error(f"优化建议生成失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def diagnose_syntax(self, input_content: str) -> Dict:
        prompt = f"""你是一个MCNP6蒙特卡罗输运代码的专家。请诊断以下MCNP6输入文件的语法错误。

输入文件内容：
```
{input_content}
```

请仔细检查以下方面的语法错误：
1. 单元格卡片（Cell Cards）语法
2. 表面卡片（Surface Cards）语法
3. 材料卡片（Material Cards）语法
4. 源定义（SDEF）语法
5. 计数卡（Tally Cards）语法
6. 数据卡（Data Cards）语法
7. 参数格式和分隔符
8. 数值范围和单位

对于每个发现的错误，请提供：
- 错误类型（如：单元格卡片错误、表面卡片错误等）
- 错误位置（行号）
- 错误描述
- 修正建议

请以JSON格式返回结果，格式如下：
```json
{{
  "has_errors": true/false,
  "errors": [
    {{
      "line": 行号,
      "type": "错误类型",
      "message": "错误描述",
      "suggestion": "修正建议"
    }}
  ],
  "warnings": [
    {{
      "line": 行号,
      "type": "警告类型",
      "message": "警告描述"
    }}
  ],
  "summary": "总体诊断总结"
}}
```

如果没有发现错误，返回 has_errors: false。"""

        try:
            result = self._generate_response(
                prompt,
                system_message="你是MCNP6代码的专家，擅长诊断语法错误并提供精确的行号和修正建议。",
                temperature=0.3
            )
            
            logger.info("语法诊断完成")
            
            import json
            try:
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    parsed_result = json.loads(json_str)
                    return {"success": True, "diagnosis": parsed_result}
                else:
                    return {"success": True, "diagnosis": {"has_errors": False, "errors": [], "warnings": [], "summary": "未发现明显的语法错误"}}
            except json.JSONDecodeError:
                return {"success": True, "diagnosis": {"has_errors": False, "errors": [], "warnings": [], "summary": result}}
            
        except Exception as e:
            logger.error(f"语法诊断失败: {str(e)}")
            return {"success": False, "error": str(e)}
