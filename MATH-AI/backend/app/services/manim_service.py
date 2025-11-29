import ast
import math
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import List, Optional
# Add this at the top of the file
def get_manim_command():
    """Get the appropriate command for running manim on the current platform"""
    if sys.platform.system() == "Windows":
        # Try to find manim in the current Python environment
        python_executable = sys.executable
        try:
            # Check if manim module is available
            import manim
            return [python_executable, "-m", "manim"]
        except ImportError:
            # Fallback to just 'manim' command
            return ["manim"]
    else:
        return ["manim"]

# Update the render_animation method
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Optional



class ManimService:
    """Service for rendering Manim animations"""

    def __init__(self):
        self.manim_path = Path(os.getenv("MANIM_PATH", "../manim"))
        self.temp_dir = Path(os.getenv("TEMP_DIR", "./temp"))
        self.temp_dir.mkdir(exist_ok=True)

        # Video quality settings with frame rate
        self.quality_settings = {
            "low": ["-l"],
            "medium": ["-m"],
            "high": ["-h"],
        }
        self.quality = os.getenv("VIDEO_QUALITY", "medium")

    def render_animation(
        self,
        manim_code: str,
        scene_name: str = "MathAnimation",
        session_id: Optional[str] = None,
    ) -> dict:
        try:
            if not session_id:
                session_id = str(uuid.uuid4())

            script_filename = f"scene_{session_id}.py"
            script_path = self.temp_dir / script_filename
            abs_script_path = Path(script_path).resolve()

            # Sanitize and write code
            processed_code = self._sanitize_manim_code(manim_code)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            with open(abs_script_path, "w", encoding="utf-8") as f:
                f.write(processed_code)

            backend_dir = Path(__file__).parent.parent.parent
            
            # ═══════════════════════════════════════════════════════════════
            # FIX: Correct command for Manim Community v0.19.0
            # ═══════════════════════════════════════════════════════════════
            
            # OLD (WRONG):
            # cmd = [sys.executable, "-m", "manim", str(abs_script_path), scene_name, "-pql"]
            
            # NEW (CORRECT for v0.19.0):
            cmd = [
                sys.executable,
                "-m",
                "manim",
                "render",  # ← ADD THIS!
                str(abs_script_path),
                scene_name,
                "--format", "mp4",
                "--media_dir", str(backend_dir / "media"),
                "-ql",  # ← Quality low (not -pql, not -m)
            ]
            
            # ═══════════════════════════════════════════════════════════════

            print(f"\n{'='*70}")
            print(f"🎬 Running Manim")
            print(f"Command: {' '.join(cmd)}")
            print(f"{'='*70}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(backend_dir),
                shell=(sys.platform == "Windows"),
            )

            if result.returncode != 0:
                print(f"❌ Manim failed!")
                print(f"STDERR: {result.stderr}")
                print(f"STDOUT: {result.stdout}")
                return {
                    "success": False,
                    "error": result.stderr or result.stdout,
                    "message": "Manim rendering failed",
                }

            print(f"✅ Manim completed successfully!")

            # Find video
            video_path = None
            search_locations = [
                backend_dir / "media" / "videos",
                self.temp_dir / "media" / "videos",
            ]
            
            for location in search_locations:
                if location.exists():
                    video_files = list(location.rglob("*.mp4"))
                    if video_files:
                        video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                        video_path = video_files[0]
                        print(f"📹 Found video at: {video_path}")
                        break

            if not video_path:
                print(f"❌ No video found!")
                return {
                    "success": False,
                    "error": "Video file not found",
                    "message": "Rendering completed but video not found",
                }

            # Copy to serving location
            videos_dir = self.temp_dir / "videos"
            videos_dir.mkdir(exist_ok=True)
            final_path = videos_dir / f"animation_{session_id}.mp4"
            
            import shutil
            shutil.copy2(video_path, final_path)
            
            print(f"📋 Copied to: {final_path}")
            print(f"🌐 URL: /videos/animation_{session_id}.mp4")
            print(f"{'='*70}\n")

            return {
                "success": True,
                "video_path": str(final_path),
                "video_url": f"/videos/animation_{session_id}.mp4",
                "session_id": session_id,
                "message": "Animation rendered successfully",
            }

        except Exception as e:
            import traceback
            print(f"\n❌ Exception:")
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "message": f"Error: {str(e)}",
            }

    def _sanitize_manim_code(self, code: str) -> str:
        """
        Normalize generated Manim code to avoid known runtime errors.

        Currently this targets FadeIn calls that pass multiple mobjects directly,
        replacing them with a single VGroup argument.
        """
        if not code:
            return code
        import re
        # Replaces .get_row_mobjects(i) with .get_rows()[i]
        code = re.sub(r'\.get_row_mobjects\(([^)]+)\)', r'.get_rows()[\1]', code)
        
        # Replaces .get_column_mobjects(i) with .get_columns()[i]
        code = re.sub(r'\.get_column_mobjects\(([^)]+)\)', r'.get_columns()[\1]', code)
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code

        line_offsets = self._compute_line_offsets(code)
        replacements: List[tuple[int, int, str]] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            # Handle both FadeIn(...) and manim.animation.fading.FadeIn(...)
            func = node.func
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr

            if func_name != "FadeIn":
                continue

            # Skip calls that already pass a single argument or use *args
            if len(node.args) <= 1:
                continue
            if any(isinstance(arg, ast.Starred) for arg in node.args):
                continue
            if not hasattr(node, "end_lineno") or node.end_lineno is None:
                continue

            arg_segments: List[str] = []
            skip_node = False
            for arg in node.args:
                segment = ast.get_source_segment(code, arg)
                if segment is None:
                    skip_node = True
                    break
                arg_segments.append(segment.strip())
            if skip_node or not arg_segments:
                continue

            # If first argument already wraps in VGroup, leave it alone
            first_arg = arg_segments[0]
            if first_arg.startswith("VGroup("):
                continue

            keyword_segments: List[str] = []
            for kw in node.keywords:
                if kw.arg is None:
                    skip_node = True
                    break
                value_segment = ast.get_source_segment(code, kw.value)
                if value_segment is None:
                    skip_node = True
                    break
                keyword_segments.append(f"{kw.arg}={value_segment.strip()}")
            if skip_node:
                continue

            replacement_parts = [f"VGroup({', '.join(arg_segments)})"]
            replacement_parts.extend(keyword_segments)
            replacement_text = f"FadeIn({', '.join(replacement_parts)})"

            start_index = self._offset_from_position(
                line_offsets, node.lineno, node.col_offset
            )
            end_index = self._offset_from_position(
                line_offsets, node.end_lineno, node.end_col_offset
            )
            replacements.append((start_index, end_index, replacement_text))

        sanitized_code = code
        if replacements:
            for start, end, replacement in sorted(replacements, reverse=True):
                sanitized_code = (
                    sanitized_code[:start] + replacement + sanitized_code[end:]
                )

        sanitized_code = self._normalize_manim_constants(sanitized_code)
        sanitized_code = self._replace_textext_with_text(sanitized_code)
        sanitized_code = self._remove_vietnamese_from_tex_text(sanitized_code)
        sanitized_code = self._fix_get_axis_labels(sanitized_code)
        return sanitized_code

    def _normalize_manim_constants(self, code: str) -> str:
        mapping = {
            "GRAY": "GREY",
        }
        for wrong, correct in mapping.items():
            code = code.replace(wrong, correct)
        return code

    def _replace_textext_with_text(self, code: str) -> str:
        """
        Replace TexText(...) with Text(..., font="Arial") to support Vietnamese.
        LaTeX cannot handle Vietnamese Unicode characters without special packages.
        """
        import re

        # Pattern: TexText("...") or TexText('...')
        # Replace with Text("...", font="Arial") or Text('...', font="Arial")
        def replace_match(match):
            quote = match.group(1)
            content = match.group(2)

            # Check if font parameter already exists in the call
            # This handles cases like TexText("...", color=RED)
            remainder = match.group(3) if match.group(3) else ""

            # If there are additional parameters, preserve them
            if remainder and not "font=" in remainder:
                return f'Text({quote}{content}{quote}, font="Arial"{remainder}'
            elif remainder and "font=" in remainder:
                # Already has font parameter, just change TexText to Text
                return f"Text({quote}{content}{quote}{remainder}"
            else:
                return f'Text({quote}{content}{quote}, font="Arial")'

        # Match TexText with double or single quotes, with optional additional parameters
        pattern = r'TexText\((["\'])([^"\']*)\1([^)]*)\)'
        sanitized = re.sub(pattern, replace_match, code)

        return sanitized

    def _remove_vietnamese_from_tex_text(self, code: str) -> str:
        """
        Remove Vietnamese text from inside Tex() \\text{...} commands.
        LaTeX's \\text{} command cannot handle Vietnamese Unicode characters.
        We strip out the problematic \\text{...} portions and add a comment
        suggesting the developer split the expression.
        """
        import re

        # Pattern to find \\text{...} inside Tex() calls that might contain Vietnamese
        vietnamese_pattern = r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]"

        # Find all Tex() calls
        tex_pattern = r'Tex\((["\'])((?:[^"\'\\]|\\.)*?)\1([^)]*)\)'

        lines = code.splitlines()
        modified_lines = []

        for line in lines:
            if "Tex(" in line:
                match = re.search(tex_pattern, line)
                if match:
                    content = match.group(2)
                    # Check if content has \\text{...} with Vietnamese
                    if ("\\text{" in content or "\\text {" in content) and re.search(
                        vietnamese_pattern, content
                    ):
                        # Add a comment before the problematic line
                        indent = len(line) - len(line.lstrip())
                        comment = (
                            " " * indent
                            + "# Note: Vietnamese text removed from LaTeX. Consider splitting into separate Text() and Tex() objects.\n"
                        )
                        modified_lines.append(comment)

                        # Remove all \\text{...} blocks
                        def replace_tex(m):
                            quote = m.group(1)
                            content = m.group(2)
                            remainder = m.group(3)
                            cleaned = re.sub(r"\\text\s*\{[^}]*\}", "", content)
                            cleaned = re.sub(r"\s+", " ", cleaned).strip()
                            return f"Tex({quote}{cleaned}{quote}{remainder})"

                        line = re.sub(tex_pattern, replace_tex, line)

            modified_lines.append(line)

        return "\n".join(modified_lines)

    def _fix_get_axis_labels(self, code: str) -> str:
        """
        This function is disabled as it is specific to ManimGL.
        The community version of Manim supports get_axis_labels with keyword arguments.
        """
        return code

    def _compute_line_offsets(self, code: str) -> List[int]:
        offsets: List[int] = []
        position = 0
        for line in code.splitlines(keepends=True):
            offsets.append(position)
            position += len(line)
        if not offsets:
            offsets.append(0)
        return offsets

    def _offset_from_position(
        self, line_offsets: List[int], lineno: int, col_offset: int
    ) -> int:
        if not line_offsets:
            return col_offset or 0
        if lineno is None or lineno <= 0:
            return col_offset or 0
        index = min(lineno - 1, len(line_offsets) - 1)
        base = line_offsets[index]
        return base + (col_offset or 0)

    def _find_output_video(self, session_id: str) -> Optional[Path]:
        """Find the rendered video file"""
        
        # Get backend directory
        backend_dir = Path(__file__).parent.parent.parent
        
        # Manim saves to backend/media by default (NOT temp!)
        media_dir = backend_dir / "media" / "videos"
        
        # Common patterns
        patterns = [
            f"animation_{session_id}.mp4",
            "MathAnimation.mp4",
        ]

        # Search in media directory (where Manim ACTUALLY saves)
        if media_dir.exists():
            for pattern in patterns:
                for video_file in media_dir.rglob(pattern):
                    return video_file
            
            # Get most recent mp4
            video_files = list(media_dir.rglob("*.mp4"))
            if video_files:
                video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                return video_files[0]
        
        # Fallback: check temp directory too
        for pattern in patterns:
            for video_file in self.temp_dir.rglob(pattern):
                return video_file

        return None

    def validate_code(self, code: str) -> dict:
        """
        Validate Manim code for basic syntax and required structure.

        Args:
            code: The code to validate

        Returns:
            dict with validation results
        """
        try:
            # Basic syntax check
            compile(code, "<string>", "exec")

            # Check for required imports
            has_import = "from manim" in code or "import manim" in code
            has_scene = "class" in code and "(Scene)" in code
            has_construct = "def construct(self)" in code

            issues = []
            if not has_import:
                issues.append("Missing 'from manim import *' or similar import")
            if not has_scene:
                issues.append("Missing Scene class definition")
            if not has_construct:
                issues.append("Missing construct() method")

            return {
                "success": len(issues) == 0,
                "valid": len(issues) == 0,
                "issues": issues,
                "message": "Code is valid" if len(issues) == 0 else "Code has issues",
            }

        except SyntaxError as e:
            return {
                "success": False,
                "valid": False,
                "error": str(e),
                "message": f"Syntax error: {str(e)}",
            }

        except Exception as e:
            return {
                "success": False,
                "valid": False,
                "error": str(e),
                "message": f"Validation error: {str(e)}",
            }

    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old temporary files

        Args:
            max_age_hours: Maximum age of files to keep (in hours)
        """
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        deleted_count = 0

        for file_path in self.temp_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Cleaned up {deleted_count} old files",
        }

    def get_video_info(self, video_path: str) -> dict:
        """
        Get information about a rendered video

        Args:
            video_path: Path to video file

        Returns:
            dict with video information
        """
        try:
            path = Path(video_path)

            if not path.exists():
                return {
                    "success": False,
                    "error": "Video file not found",
                }

            stat = path.stat()

            return {
                "success": True,
                "filename": path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


# Singleton instance
manim_service = ManimService()
