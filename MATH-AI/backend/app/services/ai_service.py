import os
import re
from typing import Optional

import google.generativeai as genai
from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables first
load_dotenv()


class AIService:
    """Service for AI-powered code generation"""

    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-3.5-turbo"
        elif self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-opus-20240229"
        elif self.provider == "gemini":
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel("gemini-2.5-flash")
            self.model = "gemini-2.5-flash"
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def generate_manim_code(self, math_text: str, additional_context: str = "") -> dict:
        """
        Generate Manim animation code from math problem text

        Args:
            math_text: Extracted math text from image
            additional_context: Additional context or instructions

        Returns:
            dict with generated code and metadata
        """
        try:
            prompt = self._build_prompt(math_text, additional_context)

            # Try up to 2 times if syntax errors occur
            max_attempts = 2
            last_error = None

            for attempt in range(max_attempts):
                if self.provider == "openai":
                    result = self._generate_with_openai(prompt)
                elif self.provider == "anthropic":
                    result = self._generate_with_anthropic(prompt)
                elif self.provider == "gemini":
                    result = self._generate_with_gemini(prompt)
                else:
                    return {
                        "success": False,
                        "error": "Invalid provider",
                        "message": "Invalid AI provider",
                    }

                if not result.get("success"):
                    return result

                # Validate syntax
                code = result.get("code", "")

                if "from manimlib import *" in code:
                    code = code.replace("from manimlib import *", "from manim import *")
                
                if "self.camera.background_color" in code:
                    code = code.replace('self.camera.background_color = "#0f172a"', 'config.background_color = "#0f172a"')
                    code = code.replace("self.camera.background_color", "config.background_color")

                result["code"] = code

                validation_error = self._validate_syntax(code)

                if validation_error is None:
                    # Success - code is valid
                    return result

                # Try to auto-fix common Vietnamese word issues
                if "must be quoted" in validation_error:
                    fixed_code = self._auto_fix_unquoted_vietnamese(
                        code, validation_error
                    )
                    if fixed_code != code:
                        # Try validating the fixed code
                        fixed_validation = self._validate_syntax(fixed_code)
                        if fixed_validation is None:
                            # Auto-fix worked!
                            result["code"] = fixed_code
                            return result

                # Syntax error - prepare for retry
                last_error = validation_error
                if attempt < max_attempts - 1:
                    # Modify prompt to emphasize syntax correctness
                    prompt = f"""LỖI CÚ PHÁP PYTHON: {validation_error}

QUAN TRỌNG: Mã trước đó có lỗi. Hãy tạo lại với cú pháp Python HOÀN TOÀN CHÍNH XÁC:
- Mọi văn bản tiếng Việt PHẢI trong dấu ngoặc kép
- Kiểm tra tất cả dấu ngoặc, dấu phẩy
- KHÔNG có biến hoặc từ tiếng Việt ngoài chuỗi

{self._build_prompt(math_text, additional_context)}"""

            # All attempts failed - return last valid code with warning
            return {
                "success": False,
                "error": str(last_error),
                "message": f"Không thể tạo mã hợp lệ sau {max_attempts} lần thử. Lỗi: {str(last_error)}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error generating code: {str(e)}",
            }

    def _build_prompt(self, math_text: str, additional_context: str = "") -> str:
        base_prompt = f"""Generate Manim Community v0.19.0 code.

    Problem: {math_text}

    CRITICAL RULES TO PREVENT RENDERING ERRORS:
    1. NO font parameter (causes white boxes!)
    2. Use font_size ONLY
    3. Keep objects away from edges (buff=0.5 minimum)
    4. Center layouts with .move_to(ORIGIN)
    5. Scale large objects with .scale(0.7)
    6. UTF-8 encoding for Vietnamese

    WORKING TEMPLATE:
    ```python
    # -*- coding: utf-8 -*-
    from manim import *

    config.background_color = "#0f172a"

    class MathAnimation(Scene):
        def construct(self):
            # Title - NO FONT PARAMETER!
            title = Text("Giải hệ phương trình", font_size=36, color=YELLOW)
            title.to_edge(UP, buff=0.5)
            self.play(Write(title))
            self.wait(1)
            
            # Equations - center them properly
            eq1 = MathTex("x + y = 5", font_size=40)
            eq2 = MathTex("2x - y = 1", font_size=40)
            
            eqs = VGroup(eq1, eq2)
            eqs.arrange(DOWN, buff=0.3)
            eqs.move_to(ORIGIN)  # Center on screen!
            
            self.play(Write(eqs))
            self.wait(2)
            
            # Matrix - scale to fit
            matrix = Matrix([[1,1,5],[2,-1,1]], h_buff=1.5, v_buff=0.8)
            matrix.scale(0.8)  # Prevent overflow
            matrix.next_to(eqs, DOWN, buff=0.8)
            
            self.play(Create(matrix))
            self.wait(2)
            
            # Answer - keep away from edge
            answer = Text("Đáp án: x=2, y=3", font_size=36, color=GREEN)
            answer.to_edge(DOWN, buff=0.5)
            
            self.play(Write(answer))
            self.wait(3)
    ```

    MANDATORY:
    - NO font="Arial" or font="Sans"
    - Use .move_to(ORIGIN) for centering
    - Use .scale(0.7-0.9) for large objects
    - Use buff=0.5 minimum
    - Add UTF-8 encoding comment

    Generate clean code:"""
        
        return base_prompt

    def _should_generate_graph(
        self, math_text: str, additional_context: str = ""
    ) -> bool:
        """Detect if graphing is needed based on input"""
        combined_text = (math_text + " " + additional_context).lower()

        # Keywords indicating graph need
        graph_keywords = [
            "đồ thị",
            "vẽ",
            "graph",
            "plot",
            "draw",
            "hàm số",
            "function",
            "parabol",
            "parabola",
            "y =",
            "f(x)",
            "g(x)",
            "y=",
            "đường cong",
            "curve",
            "biểu đồ",
            "trục",
            "axes",
            "coordinate",
        ]

        # Function patterns
        function_patterns = ["y=", "f(x)=", "g(x)=", "y =", "f(x) ="]

        # Check for keywords
        has_keyword = any(keyword in combined_text for keyword in graph_keywords)

        # Check for function patterns
        has_function = any(pattern in combined_text for pattern in function_patterns)

        return has_keyword or has_function

    def _generate_with_openai(self, prompt: str) -> dict:
        """Generate code using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Manim animator and math educator. Generate clean, well-commented, runnable Manim code.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            code = response.choices[0].message.content
            code = self._extract_code(code)

            return {
                "success": True,
                "code": code,
                "provider": "openai",
                "model": self.model,
                "message": "Code generated successfully",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"OpenAI API error: {str(e)}",
            }

    def _generate_with_anthropic(self, prompt: str) -> dict:
        """Generate code using Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )

            code = response.content[0].text
            code = self._extract_code(code)

            return {
                "success": True,
                "code": code,
                "provider": "anthropic",
                "model": self.model,
                "message": "Code generated successfully",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Anthropic API error: {str(e)}",
            }

    def _generate_with_gemini(self, prompt: str) -> dict:
        """Generate code using Google Gemini API"""
        try:
            response = self.client.generate_content(prompt)
            code = self._extract_code(response.text)

            return {
                "success": True,
                "code": code,
                "provider": "gemini",
                "model": self.model,
                "message": "Code generated successfully",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Gemini API error: {str(e)}",
            }
    import re

    def _extract_code(self, response: str) -> str:
        import re
        
        # Remove markdown
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()
        
        # Add UTF-8 declaration
        if "# -*- coding: utf-8 -*-" not in code:
            code = "# -*- coding: utf-8 -*-\n" + code
        
        # Remove ALL font parameters (causes white boxes)
        code = re.sub(r',?\s*font\s*=\s*["\'][^"\']*["\']', '', code)
        
        # Fix other issues
        code = code.replace("from manimlib import *", "from manim import *")
        code = code.replace("ShowCreation(", "Create(")
        code = re.sub(r',?\s*v_lines\s*=\s*\[[^\]]*\]', '', code)
        code = re.sub(r',?\s*h_lines\s*=\s*\[[^\]]*\]', '', code)
        
        # Remove Vietnamese comments
        lines = []
        for line in code.split("\n"):
            if "#" in line and any(ord(c) > 127 for c in line):
                if line.strip().startswith("#") and "coding" not in line:
                    continue
                line = line.split("#")[0].rstrip()
            lines.append(line)
        code = "\n".join(lines)
        
        # Ensure imports
        if "from manim import *" not in code:
            code = "from manim import *\n\n" + code
        
        return code


    # ═══════════════════════════════════════════════════════
    # ADDITIONAL HELPER METHOD (add this too)
    # ═══════════════════════════════════════════════════════

    def _validate_manim_code(self, code: str) -> dict:
        """
        Validate Manim code for common issues
        Returns dict with validation results
        """
        issues = []
        
        # Check for wrong imports
        if "from manimlib" in code:
            issues.append("Using 'from manimlib' instead of 'from manim'")
        
        # Check for self.camera
        if "self.camera" in code:
            issues.append("Using self.camera (not supported in Community)")
        
        # Check for ShowCreation
        if "ShowCreation" in code:
            issues.append("Using ShowCreation (should be Create)")
        
        # Check for v_lines in Matrix
        if "v_lines" in code and "Matrix" in code:
            issues.append("Using v_lines in Matrix (not supported)")
        
        # Check for h_lines in Matrix
        if "h_lines" in code and "Matrix" in code:
            issues.append("Using h_lines in Matrix (not supported)")
        
        # Check for config placement
        if "config.background_color" in code and "class MathAnimation" in code:
            config_pos = code.find("config.background_color")
            class_pos = code.find("class MathAnimation")
            if config_pos > class_pos:
                issues.append("config.background_color after class definition (should be before)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "message": "Code is valid" if len(issues) == 0 else f"Found {len(issues)} issues"
        }


    def _validate_syntax(self, code: str) -> Optional[str]:
        """
        Validate Python syntax of generated code.
        Uses AST to detect Vietnamese variable names that should be quoted strings.

        Returns:
            None if valid, error message string if invalid
        """
        import ast

        try:
            # First check basic syntax
            tree = ast.parse(code)

            # Check for Vietnamese variable names using AST
            vietnamese_chars = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ"

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    # Check if the variable name contains Vietnamese characters
                    if any(c in vietnamese_chars for c in node.id):
                        return f"Vietnamese word '{node.id}' must be quoted. Add quotes around '{node.id}'"

            return None

        except SyntaxError as e:
            return f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return f"Validation error: {str(e)}"

    def _auto_fix_unquoted_vietnamese(self, code: str, error: str) -> str:
        """
        Attempt to automatically fix ALL unquoted Vietnamese words in generated code.
        """
        import ast
        import re

        vietnamese_chars = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ"

        # Find all Vietnamese variable names
        try:
            tree = ast.parse(code)
            vietnamese_words = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if any(c in vietnamese_chars for c in node.id):
                        vietnamese_words.add(node.id)

            if not vietnamese_words:
                return code

            # Fix all Vietnamese words
            lines = code.splitlines()
            fixed_lines = []

            for line in lines:
                # Skip comments
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    fixed_lines.append(line)
                    continue

                fixed_line = line

                # Fix each Vietnamese word found
                for word in vietnamese_words:
                    if word in fixed_line:
                        # Patterns to match unquoted Vietnamese words
                        patterns = [
                            (rf"(=\s*)({word})(\s*$)", rf'\1"{word}"\3'),
                            (rf"(=\s*)({word})(\s)", rf'\1"{word}"\3'),
                            (rf"(\(\s*)({word})(\s*\))", rf'\1"{word}"\3'),
                            (rf"(\[\s*)({word})(\s*\])", rf'\1"{word}"\3'),
                            (rf"(,\s*)({word})(\s*$)", rf'\1"{word}"\3'),
                            (rf"(,\s*)({word})(\s)", rf'\1"{word}"\3'),
                            (rf"^(\s*)({word})(\s*$)", rf'\1"{word}"\3'),
                            (rf"(\s)({word})(\s)", rf'\1"{word}"\3'),
                        ]

                        for pattern, replacement in patterns:
                            fixed_line = re.sub(pattern, replacement, fixed_line)

                fixed_lines.append(fixed_line)

            return "\n".join(fixed_lines)

        except Exception:
            # If AST parsing fails, return original code
            return code

    def improve_code(self, code: str, feedback: str) -> dict:
        """
        Improve existing Manim code based on feedback

        Args:
            code: Current Manim code
            feedback: User feedback or error messages

        Returns:
            dict with improved code
        """
        try:
            prompt = f"""Hãy cải thiện đoạn mã ManimGL sau dựa trên góp ý dưới đây, đảm bảo toàn bộ nội dung hiển thị trong video là tiếng Việt và tiếp tục tập trung vào giải phương trình lượng giác cho kỳ thi THPT Quốc gia lớp 12.

Góp ý: {feedback}

Mã hiện tại:
```python
{code}
```

Xuất ra phiên bản Python hoàn chỉnh đã chỉnh sửa, không kèm markdown hay giải thích."""

            if self.provider == "openai":
                return self._generate_with_openai(prompt)
            elif self.provider == "anthropic":
                return self._generate_with_anthropic(prompt)
            elif self.provider == "gemini":
                return self._generate_with_gemini(prompt)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error improving code: {str(e)}",
            }

    def classify_input(self, user_input: str) -> dict:
        """
        Classify user input to determine if it contains math content
        and what type of response is appropriate

        Args:
            user_input: User's text input

        Returns:
            dict with classification results
        """
        try:
            prompt = f"""Phân loại nội dung đầu vào sau đây. Trả lời theo định dạng JSON chính xác:

Nội dung: "{user_input}"

Phân tích và trả về JSON với cấu trúc:
{{
    "is_math": true/false,
    "content_type": "greeting/casual/math_problem/math_question/unclear",
    "suggested_action": "chat/explain/answer/animate",
    "confidence": 0.0-1.0,
    "reason": "lý do ngắn gọn"
}}

Quy tắc phân loại:
- is_math = true nếu có: phương trình, biểu thức toán, bài toán, hỏi về toán
- content_type:
  * "greeting": chào hỏi (hi, hello, xin chào)
  * "casual": câu hỏi thường (bạn là ai, help me)
  * "math_problem": bài toán cụ thể (giải x^2+1=0, tính tích phân)
  * "math_question": hỏi về khái niệm toán (đạo hàm là gì?)
  * "unclear": không rõ ràng
- suggested_action:
  * "chat": trả lời thông thường (greeting, casual)
  * "explain": giải thích khái niệm (math_question)
  * "answer": giải bài toán nhanh (math_problem ngắn)
  * "animate": tạo video (math_problem phức tạp)

Chỉ trả về JSON, không thêm text nào khác."""

            if self.provider == "gemini":
                response = self.client.generate_content(prompt)
                result_text = response.text.strip()

                # Extract JSON from response
                import json
                import re

                # Try to find JSON in response
                json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(result_text)

                return {
                    "success": True,
                    "is_math": result.get("is_math", False),
                    "content_type": result.get("content_type", "unclear"),
                    "suggested_action": result.get("suggested_action", "chat"),
                    "confidence": result.get("confidence", 0.5),
                    "reason": result.get("reason", ""),
                }
            else:
                # Fallback for non-Gemini providers
                return self._classify_with_keywords(user_input)

        except Exception as e:
            print(f"Classification error: {e}")
            # Fallback to keyword-based classification
            return self._classify_with_keywords(user_input)

    def _classify_with_keywords(self, user_input: str) -> dict:
        """Fallback keyword-based classification"""
        user_lower = user_input.lower()

        # Check for greetings
        greetings = ["hi", "hello", "xin chào", "chào", "hey"]
        if any(g in user_lower for g in greetings):
            return {
                "success": True,
                "is_math": False,
                "content_type": "greeting",
                "suggested_action": "chat",
                "confidence": 0.9,
                "reason": "Detected greeting",
            }

        # Check for math symbols/keywords
        math_indicators = [
            "=",
            "+",
            "-",
            "*",
            "/",
            "^",
            "x^",
            "sin",
            "cos",
            "tan",
            "log",
            "integral",
            "derivative",
            "tích phân",
            "đạo hàm",
            "phương trình",
            "giải",
            "tính",
            "solve",
            "calculate",
        ]

        has_math = any(indicator in user_lower for indicator in math_indicators)

        if has_math:
            return {
                "success": True,
                "is_math": True,
                "content_type": "math_problem",
                "suggested_action": "answer",
                "confidence": 0.7,
                "reason": "Detected math keywords",
            }

        # Default: casual conversation
        return {
            "success": True,
            "is_math": False,
            "content_type": "casual",
            "suggested_action": "chat",
            "confidence": 0.6,
            "reason": "No math content detected",
        }

    def detect_intent(self, user_input: str) -> dict:
        """
        Detect user intent: explain, answer, or animate
        (Deprecated: Use classify_input instead)

        Args:
            user_input: User's text input

        Returns:
            dict with intent type and confidence
        """
        classification = self.classify_input(user_input)
        return {
            "intent": classification.get("suggested_action", "chat"),
            "confidence": classification.get("confidence", 0.5),
        }

    def chat_response(self, user_input: str) -> dict:
        """
        Generate a conversational response for non-math content

        Args:
            user_input: User's input text

        Returns:
            dict with chat response
        """
        try:
            prompt = f"""Bạn là trợ lý AI thân thiện chuyên về toán học. Trả lời HOÀN TOÀN BẰNG TIẾNG VIỆT.

Người dùng nói: "{user_input}"

Hướng dẫn trả lời:
- Nếu là lời chào: Chào lại thân thiện và giới thiệu bạn có thể giúp gì về toán học
- Nếu hỏi về khả năng: Giải thích bạn có thể giải toán, tạo video giảng dạy
- Nếu không liên quan toán: Lịch sự chuyển hướng về toán học
- Luôn nhiệt tình và khuyến khích học toán

Trả lời ngắn gọn (2-3 câu), thân thiện bằng tiếng Việt:"""

            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a friendly math tutor assistant who responds in Vietnamese.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=300,
                )
                answer = response.choices[0].message.content

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}],
                )
                answer = response.content[0].text

            elif self.provider == "gemini":
                response = self.client.generate_content(prompt)
                answer = response.text

            return {
                "success": True,
                "response": answer,
                "message": "Chat response generated successfully",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error generating chat response: {str(e)}",
            }

    def quick_answer(self, math_text: str, user_question: str = "") -> dict:
        """
        Generate a quick text answer without animation

        Args:
            math_text: Mathematical content
            user_question: Optional specific question

        Returns:
            dict with answer text
        """
        try:
            if user_question:
                prompt = f"""Bạn là gia sư toán học Việt Nam. Trả lời HOÀN TOÀN BẰNG TIẾNG VIỆT câu hỏi sau:

Bài toán: {math_text}

Câu hỏi: {user_question}

Yêu cầu:
- Trả lời 100% bằng tiếng Việt
- Ngắn gọn, dễ hiểu
- Nếu cần giải, trình bày các bước chính
- Dùng ký hiệu toán học chuẩn"""
            else:
                prompt = f"""Bạn là gia sư toán học Việt Nam. Giải bài toán sau HOÀN TOÀN BẰNG TIẾNG VIỆT:

Bài toán: {math_text}

Trả lời bằng tiếng Việt theo cấu trúc:
1. **Phương pháp:** (tóm tắt cách giải)
2. **Các bước giải:**
   - Bước 1: ...
   - Bước 2: ...
   - Bước 3: ...
3. **Đáp án:** (kết quả cuối cùng)

Lưu ý: Tất cả giải thích và nhận xét đều phải bằng tiếng Việt."""

            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful math tutor who responds in Vietnamese.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=800,
                )
                answer = response.choices[0].message.content

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}],
                )
                answer = response.content[0].text

            elif self.provider == "gemini":
                response = self.client.generate_content(prompt)
                answer = response.text

            return {
                "success": True,
                "answer": answer,
                "message": "Answer generated successfully",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error generating answer: {str(e)}",
            }

    def explain_math(self, math_text: str) -> dict:
        """
        Generate a step-by-step explanation of a math problem

        Args:
            math_text: Mathematical content to explain

        Returns:
            dict with explanation
        """
        try:
            prompt = f"""Bạn là giáo viên toán Việt Nam chuyên luyện thi THPT Quốc gia. Giải thích bài toán sau HOÀN TOÀN BẰNG TIẾNG VIỆT:

━━━━━━━━━━━━━━━━━━━━━━━━
📚 BÀI TOÁN
━━━━━━━━━━━━━━━━━━━━━━━━

{math_text}

━━━━━━━━━━━━━━━━━━━━━━━━
✍️ YÊU CẦU GIẢI THÍCH
━━━━━━━━━━━━━━━━━━━━━━━━

Trình bày 100% bằng tiếng Việt theo cấu trúc:

**1. PHÂN TÍCH ĐỀ BÀI**
- Xác định dạng toán
- Những gì đã cho và cần tìm
- Điều kiện (nếu có)

**2. KIẾN THỨC CẦN SỬ DỤNG**
- Công thức liên quan
- Định lý, tính chất cần áp dụng
- Phương pháp giải

**3. CÁC BƯỚC GIẢI CHI TIẾT**
- Bước 1: ... (giải thích tại sao làm bước này)
- Bước 2: ... (biến đổi và giải thích)
- Bước 3: ... (tiếp tục đến khi có kết quả)

**4. KẾT LUẬN**
- Đáp án cuối cùng
- Kiểm tra (nếu cần)
- Nhận xét về bài toán

Lưu ý:
✓ Giải thích dễ hiểu như đang dạy học sinh
✓ Nêu rõ lý do của mỗi bước
✓ Dùng thuật ngữ chuẩn trong SGK
✓ Tất cả nội dung phải bằng tiếng Việt
✓ Sử dụng ký hiệu toán học chuẩn"""

            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful math tutor who explains in Vietnamese.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1200,
                )
                explanation = response.choices[0].message.content

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1200,
                    messages=[{"role": "user", "content": prompt}],
                )
                explanation = response.content[0].text

            elif self.provider == "gemini":
                response = self.client.generate_content(prompt)
                explanation = response.text

            return {
                "success": True,
                "explanation": explanation,
                "message": "Explanation generated successfully",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error generating explanation: {str(e)}",
            }


# Singleton instance
ai_service = AIService()
