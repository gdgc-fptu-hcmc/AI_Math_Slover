import os
import re
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY not found. AI features will fail.")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash-lite" # Or "gemini-2.0-flash-thinking-exp" if available

    def chat_turn(self, history: list, files: list, animate: bool = False) -> dict:
        """
        Process a chat turn with history and files.
        """
        # 1. Prepare System Instruction
        if animate:
            system_instruction = """You are a Manim Animation Expert. 
            The user wants to visualize a math concept.
            
            RULES:
            1. Output ONLY a valid Python code block for Manim Community v0.19.0.
            2. The class must be named `MathAnimation(Scene)`.
            3. Use `config.background_color = "#0f172a"`.
            4. NO external assets (SVG/Images). Use standard shapes (Circle, Square, etc.).
            5. Explain the math briefly in comments, but the output must be PURE CODE in a markdown block.
            """
        else:
            system_instruction = """You are an expert Math Tutor.
            Solve the problem step-by-step.
            - If the user provides an image/PDF, analyze it thoroughly.
            - Use LaTeX for math formulas (enclose in $...$).
            - Be concise, encouraging, and clear.
            """

        # 2. Build Content List
        contents = []
        
        # Add history (excluding system messages for simplicity in this implementation)
        for msg in history:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

        # Add current turn content
        current_parts = []
        
        # Add text prompt
        user_text = history[-1]["content"] if history else "Analyze this."
        if animate:
            user_text += "\n\n(Generate Manim Python code for this)"
        
        current_parts.append(types.Part.from_text(text=user_text))

        # Add files (Images/PDFs)
        for file_data in files:
            current_parts.append(types.Part.from_bytes(
                data=file_data["data"],
                mime_type=file_data["mime_type"]
            ))

        # Replace the last message with the multimodal one
        if contents and contents[-1].role == "user":
            contents.pop()
        
        contents.append(types.Content(role="user", parts=current_parts))

        # 3. Generate Response
        try:
            generate_config = types.GenerateContentConfig(
                temperature=0.1 if animate else 0.7,
                system_instruction=[types.Part.from_text(text=system_instruction)],
                # thinking_config={"thinking_budget": 1024} # Optional if using thinking model
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_config
            )

            response_text = response.text

            # 4. Post-processing
            if animate:
                # Extract code block
                code_match = re.search(r"```python(.*?)```", response_text, re.DOTALL)
                if code_match:
                    code = code_match.group(1).strip()
                    return {"type": "code", "content": code}
                else:
                    # Fallback if model just chatted instead of coding
                    return {"type": "text", "content": "I couldn't generate the animation code. Here is the explanation instead:\n\n" + response_text}
            
            return {"type": "text", "content": response_text}

        except Exception as e:
            print(f"GenAI Error: {e}")
            return {"type": "error", "content": str(e)}

ai_service = AIService()