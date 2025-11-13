import os
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
        """Build the prompt for code generation"""

        # Detect if graphing is needed
        needs_graph = self._should_generate_graph(math_text, additional_context)

        graph_instruction = ""
        if needs_graph:
            graph_instruction = """
YÊU CẦU ĐỒ THỊ!
- Bắt buộc vẽ đồ thị hoặc biểu diễn hàm số phù hợp
- Dùng axes = Axes() để tạo hệ trục toạ độ
- Dùng axes.get_graph() để vẽ hàm và lựa chọn miền hợp lý
- Ghi nhãn trục và điểm quan trọng bằng tiếng Việt (dùng Text với font="Arial")
- Hiển thị phương trình hoặc hàm ngay cạnh đồ thị
"""

        base_prompt = f"""Bạn là một giáo viên toán Việt Nam chuyên luyện thi THPT Quốc gia. Tạo mã ManimGL với 100% nội dung hiển thị bằng TIẾNG VIỆT để giảng dạy bài toán sau.

Nội dung toán học:
{math_text}

{f"Ngữ cảnh bổ sung: {additional_context}" if additional_context else ""}

{graph_instruction}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YÊU CẦU TIẾNG VIỆT (BẮT BUỘC 100%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ MỌI văn bản giải thích PHẢI bằng tiếng Việt:
   - Tiêu đề: "Giải phương trình", "Tìm đạo hàm", "Tính tích phân"
   - Các bước: "Bước 1: Biến đổi", "Bước 2: Giải phương trình"
   - Nhận xét: "Ta có", "Suy ra", "Vậy", "Kết luận"
   - Chú thích đồ thị: "Đồ thị hàm số", "Điểm cực trị", "Tiệm cận"

2. ✅ Cách sử dụng Text và Tex ĐÚNG:

   ✓ ĐÚNG - Văn bản tiếng Việt:
   Text("Giải phương trình bậc hai", font="Arial", color=YELLOW)
   Text("Bước 1: Biến đổi phương trình", font="Arial")
   Text("Ta có: Δ = b² - 4ac", font="Arial")

   ✓ ĐÚNG - Công thức toán học (không có chữ):
   Tex("x^2 + 2x + 1 = 0")
   Tex("\\\\Delta = b^2 - 4ac")
   Tex("x = \\\\frac{{-b \\\\pm \\\\sqrt{{\\\\Delta}}}}{{2a}}")

   ✓ ĐÚNG - Kết hợp tiếng Việt và công thức:
   giai_thich = Text("Phương trình có nghiệm:", font="Arial")
   nghiem = Tex("x_1 = -1, \\\\quad x_2 = -1")
   VGroup(giai_thich, nghiem).arrange(DOWN)

   ✗ SAI - KHÔNG BAO GIỜ làm thế này:
   Tex("x = 0 \\\\text{{hoặc}} x = 1")  # ✗ LaTeX không hỗ trợ tiếng Việt
   Tex("Giải: x^2 = 4")  # ✗ Chữ tiếng Việt trong Tex
   TexText("Bước 1")  # ✗ TexText không tồn tại trong ManimGL

3. ✅ Cấu trúc video bằng tiếng Việt:
   - Mở đầu: Giới thiệu bài toán bằng Text()
   - Nội dung: Các bước giải thích bằng Text() + công thức bằng Tex()
   - Kết thúc: Kết luận và đáp án bằng Text()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 QUY TẮC MANIMGL (NGHIÊM NGẶT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Import: from manimlib import *
• Văn bản tiếng Việt: Text("nội dung", font="Arial", color=...)
• Công thức toán: Tex("x^2 + y^2 = r^2")
• Đồ thị: axes = Axes(); graph = axes.get_graph(lambda x: ...)
• Nhãn trục: Text("Trục hoành", font="Arial").next_to(axes.x_axis, DOWN)
• Màu sắc: BLUE, RED, GREEN, YELLOW, ORANGE, PURPLE, GREY
• Hiệu ứng: Write(), FadeIn(), Transform(), ShowCreation()
• Định vị: .to_edge(UP), .shift(DOWN*2), .next_to(obj, RIGHT)
• Thời gian: self.wait(2-3) sau mỗi bước quan trọng
• Tổng thời lượng: Tối thiểu 18 giây

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 MẪU CODE CHUẨN (100% TIẾNG VIỆT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```python
from manimlib import *

class MathAnimation(Scene):
    def construct(self):
        # Tiêu đề bằng tiếng Việt
        tieu_de = Text("Giải phương trình bậc hai", font="Arial", color=YELLOW)
        tieu_de.to_edge(UP)
        self.play(Write(tieu_de), run_time=2)
        self.wait(2)

        # Đề bài - công thức toán học
        de_bai = Tex("x^2 + 5x + 6 = 0", color=WHITE).scale(1.2)
        de_bai.next_to(tieu_de, DOWN, buff=1)
        self.play(Write(de_bai), run_time=2)
        self.wait(2)

        # Bước 1 - giải thích bằng tiếng Việt
        buoc1_text = Text("Bước 1: Tìm delta", font="Arial", color=BLUE)
        buoc1_text.next_to(de_bai, DOWN, buff=1)
        self.play(FadeIn(buoc1_text), run_time=1.5)
        self.wait(2)

        # Công thức delta
        delta_formula = Tex("\\\\Delta = b^2 - 4ac", color=WHITE)
        delta_formula.next_to(buoc1_text, DOWN)
        self.play(Write(delta_formula), run_time=2)
        self.wait(2)

        # Tính toán
        delta_value = Tex("\\\\Delta = 25 - 24 = 1", color=GREEN)
        delta_value.next_to(delta_formula, DOWN)
        self.play(Write(delta_value), run_time=2)
        self.wait(2)

        # Bước 2
        buoc2_text = Text("Bước 2: Tìm nghiệm", font="Arial", color=BLUE)
        buoc2_text.move_to(buoc1_text.get_center())
        self.play(
            FadeOut(buoc1_text),
            FadeOut(delta_formula),
            FadeOut(delta_value),
            FadeIn(buoc2_text),
            run_time=2
        )
        self.wait(2)

        # Công thức nghiệm
        nghiem_formula = Tex("x = \\\\frac{{-b \\\\pm \\\\sqrt{{\\\\Delta}}}}{{2a}}")
        nghiem_formula.next_to(buoc2_text, DOWN)
        self.play(Write(nghiem_formula), run_time=2)
        self.wait(2)

        # Kết quả
        ket_qua = Text("Vậy phương trình có 2 nghiệm:", font="Arial", color=ORANGE)
        nghiem1 = Tex("x_1 = -2", color=GREEN)
        nghiem2 = Tex("x_2 = -3", color=GREEN)

        ket_qua.move_to(buoc2_text.get_center())
        nghiem_group = VGroup(nghiem1, nghiem2).arrange(RIGHT, buff=1)
        nghiem_group.next_to(ket_qua, DOWN)

        self.play(
            FadeOut(buoc2_text),
            FadeOut(nghiem_formula),
            FadeIn(ket_qua),
            run_time=2
        )
        self.wait(1)
        self.play(Write(nghiem_group), run_time=2)
        self.wait(3)
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ LƯU Ý QUAN TRỌNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Trả về DUY NHẤT mã Python, không kèm ```python hoặc giải thích
✓ Luôn bắt đầu: from manimlib import *
✓ Luôn dùng: class MathAnimation(Scene):
✓ Mọi Text đều có font="Arial" để hiển thị tiếng Việt đúng
✓ Tách biệt: Text() cho chữ, Tex() cho công thức
✓ Thời lượng tối thiểu 18 giây (dùng self.wait())
✓ Màu sắc rõ ràng để phân biệt các phần

Hãy tạo mã ngay bây giờ với 100% nội dung tiếng Việt:"""

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

    def _extract_code(self, response: str) -> str:
        """Extract Python code from AI response"""
        # Remove markdown code blocks if present
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()

        return code

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

    def detect_intent(self, user_input: str) -> dict:
        """
        Detect user intent: explain, answer, or animate

        Args:
            user_input: User's text input

        Returns:
            dict with intent type and confidence
        """
        try:
            user_input_lower = user_input.lower()

            # Keywords for different intents
            explain_keywords = [
                "giải thích",
                "explain",
                "hướng dẫn",
                "phân tích",
                "tại sao",
                "why",
            ]
            answer_keywords = [
                "giải",
                "solve",
                "tính",
                "calculate",
                "bao nhiêu",
                "what is",
                "kết quả",
            ]
            animate_keywords = [
                "animation",
                "video",
                "minh họa",
                "vẽ",
                "draw",
                "show",
                "visualize",
            ]

            # Check for explicit keywords
            has_explain = any(
                keyword in user_input_lower for keyword in explain_keywords
            )
            has_answer = any(keyword in user_input_lower for keyword in answer_keywords)
            has_animate = any(
                keyword in user_input_lower for keyword in animate_keywords
            )

            # Determine intent
            if has_animate:
                return {"intent": "animate", "confidence": 0.9}
            elif has_explain and not has_answer:
                return {"intent": "explain", "confidence": 0.8}
            elif has_answer:
                return {"intent": "answer", "confidence": 0.8}
            else:
                # Default to answer for math content
                return {"intent": "answer", "confidence": 0.6}

        except Exception as e:
            return {"intent": "answer", "confidence": 0.5}

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
