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
- Ghi nhãn trục và điểm quan trọng bằng tiếng Việt
- Hiển thị phương trình hoặc hàm ngay cạnh đồ thị
"""

        base_prompt = f"""Bạn là một giáo viên toán Việt Nam chuyên luyện thi THPT Quốc gia lớp 12 về chủ đề giải phương trình lượng giác. Luôn tạo mã ManimGL ngắn gọn, rõ ràng để dẫn dắt học sinh giải một bài toán phương trình lượng giác điển hình, ngay cả khi nội dung đầu vào ở ngôn ngữ khác.

Nội dung toán học đầu vào:
{math_text}

{f"Ngữ cảnh bổ sung: {additional_context}" if additional_context else ""}

{graph_instruction}

YÊU CẦU CHUNG:
1. Toàn bộ văn bản hiển thị trong video (Tex, Text, chú thích) phải bằng tiếng Việt chuẩn và phần mở đầu phải giới thiệu bài toán bằng tiếng Việt.
2. Bố cục rõ ràng: Nêu bài toán → Chiến lược xử lý → Các bước giải → Kết luận nghiệm.
3. Luôn nhấn mạnh phương pháp giải phương trình lượng giác lớp 12 (hạ bậc, đặt ẩn phụ t = tan(x/2), dùng công thức cộng/trừ, v.v.). Nếu đề bài không thuộc dạng này, hãy chuyển bài toán về một phương trình lượng giác tương đương trước khi giải.
4. Nếu cần minh họa hàm số/đồ thị, bắt buộc vẽ bằng axes = Axes() và chú thích bằng tiếng Việt.
5. Nhãn điểm, bước giải, lời bình đều phải bằng tiếng Việt và bám sát ngữ cảnh luyện thi THPT.

QUY TẮC MANIMGL (QUAN TRỌNG):
• Import: from manimlib import *
• Biểu thức toán học: Tex("sin^2 x + cos^2 x = 1") — chỉ dùng cho công thức LaTeX không có chữ tiếng Việt
• Văn bản tiếng Việt: BẮT BUỘC dùng Text("Chiến lược giải", font="Arial") — KHÔNG BAO GIỜ dùng TexText cho tiếng Việt vì LaTeX không hỗ trợ Unicode Việt
• NGHIÊM CẤM dùng \\text{{...}} bên trong Tex() để chứa tiếng Việt (ví dụ: KHÔNG dùng Tex("x = 0 \\\\text{{hoặc}} x = 1"))
• Khi cần kết hợp công thức và văn bản tiếng Việt, hãy tách thành nhiều đối tượng riêng biệt hoặc dùng VGroup
• Luôn đặt font="Arial" hoặc font tương tự khi dùng Text để hiển thị tiếng Việt có dấu chính xác
• Đồ thị: axes = Axes(); graph = axes.get_graph(lambda x: ...)
• Nhãn trục: Tạo riêng bằng Tex("x").next_to(axes.x_axis, DOWN) và Tex("y").next_to(axes.y_axis, LEFT) — KHÔNG dùng get_axis_labels(x_label=..., y_label=...)
• Nhãn đồ thị: dùng Tex().next_to(...); không dùng get_graph_label()
• Màu sắc: BLUE, RED, GREEN, YELLOW, ORANGE, PURPLE, GREY (không dùng GRAY)
• Hiệu ứng: Write(), FadeIn(), Transform(), ShowCreation() (không dùng Create!) — với FadeIn chỉ truyền một Mobject hoặc gói chung bằng VGroup khi cần nhiều đối tượng, KHÔNG đặt scale_factor tùy chỉnh
• Định vị: .to_edge(UP/DOWN/LEFT/RIGHT), .shift(UP/DOWN), .next_to(obj, DOWN)
• Biến đổi Mobject: dùng .animate hoặc Animation tương ứng, không truyền Mobject trực tiếp vào self.play

PHONG CÁCH MÃ:
✓ Tên biến ngắn gọn, dễ hiểu (van_de, buoc1, ket_luan, do_thi)
✓ Chú thích ngắn bằng tiếng Việt giải thích các phần chính
✓ Gom nhóm thao tác liên quan
✓ Dùng self.wait(2-3) cho các điểm quan trọng; tổng thời lượng tối thiểu 18 giây
✓ Dùng run_time=2 hoặc run_time=3 để làm chậm hoạt ảnh quan trọng
✓ Với đồ thị: self.play(ShowCreation(graph), run_time=3) và self.wait(4) để học sinh quan sát
✓ Giữ tổng số dòng ≤ 65 nếu có thể

MẪU MINH HỌA (VĂN BẢN TIẾNG VIỆT):
```python
from manimlib import *

class MathAnimation(Scene):
    def construct(self):
        # Giới thiệu bài toán
        tieu_de = Text("Giải phương trình lượng giác", color=YELLOW)
        tieu_de.to_edge(UP)
        bai_toan = Tex("2\\\\sin x + \\\\sqrt{{3}}\\\\cos x = 1")
        bai_toan.next_to(tieu_de, DOWN)

        self.play(Write(tieu_de), Write(bai_toan), run_time=2)
        self.wait(2)

        # Chiến lược giải
        chien_luoc = Text("Đặt \\\\tan \\\\frac{{x}}{{2}} = t", color=BLUE).scale(0.9)
        chien_luoc.next_to(bai_toan, DOWN, buff=0.6)
        self.play(FadeIn(chien_luoc), run_time=2)
        self.wait(2)

        # Kết luận
        ket_luan = Tex("x = \\\\frac{{\\\\pi}}{{6}} + k2\\\\pi", color=GREEN).scale(1.1)
        ket_luan.move_to(ORIGIN)
        self.play(Transform(bai_toan, ket_luan), run_time=2)
        self.wait(4)
```

LƯU Ý QUAN TRỌNG:
- Trả về duy nhất mã Python, không kèm markdown hay giải thích.
- Luôn bắt đầu bằng 'from manimlib import *' và dùng lớp MathAnimation.
- Nếu có hàm số, đảm bảo đồ thị xuất hiện ít nhất 4 giây.
- Kết luận phải ghi rõ nghiệm bằng tiếng Việt.
- Giữ đúng mạch: Giới thiệu → Chiến lược → Giải từng bước → Kết luận → (Tùy chọn) Đồ thị.

Tạo mã ngay bây giờ:"""

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
                prompt = f"""Bạn là gia sư toán học. Trả lời câu hỏi sau về bài toán này:

Bài toán: {math_text}

Câu hỏi: {user_question}

Trả lời ngắn gọn, rõ ràng bằng tiếng Việt. Nếu cần giải, hãy trình bày các bước chính."""
            else:
                prompt = f"""Bạn là gia sư toán học. Giải bài toán sau và đưa ra đáp án:

{math_text}

Trả lời:
1. Phương pháp giải (ngắn gọn)
2. Các bước chính
3. Đáp án cuối cùng

Trình bày rõ ràng, súc tích bằng tiếng Việt."""

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
            prompt = f"""Giải thích bài toán sau hoàn toàn bằng tiếng Việt theo phong cách giáo viên luyện thi THPT Quốc gia lớp 12:

{math_text}

Trình bày:
1. Nhận định đề bài và yêu cầu
2. Kiến thức cần sử dụng
3. Các bước giải chi tiết (nếu là bài tập)
4. Giải thích ý nghĩa của các khái niệm (nếu là lý thuyết)
5. Kết luận và đáp án cuối cùng

Diễn đạt rõ ràng, chuẩn chính tả, dùng thuật ngữ quen thuộc trong chương trình THPT."""

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
