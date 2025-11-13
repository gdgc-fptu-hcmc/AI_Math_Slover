import ast
import math
import os
import subprocess
import tempfile
import threading
import uuid
from pathlib import Path
from typing import List, Optional


class ManimService:
    """Service for rendering Manim animations"""

    def __init__(self):
        self.manim_path = Path(os.getenv("MANIM_PATH", "../manim"))
        self.temp_dir = Path(os.getenv("TEMP_DIR", "./temp"))
        self.temp_dir.mkdir(exist_ok=True)

        # Video quality settings with frame rate
        self.quality_settings = {
            "low": ["-ql"],
            "medium": ["-qm"],
            "high": ["-qh"],
        }
        self.quality = os.getenv("VIDEO_QUALITY", "medium")

        background_music_dir = os.getenv("BACKGROUND_MUSIC_DIR")
        default_audio_dir = Path(__file__).parent.parent / "assets" / "audio"
        self.audio_dir = (
            Path(background_music_dir) if background_music_dir else default_audio_dir
        )
        self.audio_tracks = (
            sorted(self.audio_dir.glob("*.mp3")) if self.audio_dir.exists() else []
        )
        self._audio_index = 0
        self._audio_lock = threading.Lock()
        self.background_music_enabled = (
            os.getenv("ENABLE_BACKGROUND_MUSIC", "true").lower() != "false"
        )
        try:
            self.music_volume = float(os.getenv("BACKGROUND_MUSIC_VOLUME", "0.2"))
        except ValueError:
            self.music_volume = 0.2

    def render_animation(
        self,
        manim_code: str,
        scene_name: str = "MathAnimation",
        session_id: Optional[str] = None,
    ) -> dict:
        """
        Render Manim animation from code

        Args:
            manim_code: Python code containing Manim scene
            scene_name: Name of the scene class to render
            session_id: Optional session ID for file naming

        Returns:
            dict with render results and video path
        """
        try:
            # Generate unique filename
            if not session_id:
                session_id = str(uuid.uuid4())

            script_filename = f"scene_{session_id}.py"
            script_path = self.temp_dir / script_filename

            # Get absolute paths
            abs_script_path = script_path.resolve()
            abs_temp_dir = self.temp_dir.resolve()

            # Sanitize code before writing to disk to guard against common runtime issues
            processed_code = self._sanitize_manim_code(manim_code)

            with open(abs_script_path, "w", encoding="utf-8") as f:
                f.write(processed_code)

            # Prepare render command
            quality_flags = self.quality_settings.get(self.quality, ["-qm"])

            # Use manimgl command with absolute paths
            cmd = [
                "manimgl",
                str(abs_script_path),
                scene_name,
                "-w",  # Write to file
                "--video_dir",
                str(abs_temp_dir),
                "--file_name",
                f"animation_{session_id}",
            ]
            cmd += [str(flag) for flag in quality_flags]

            # Run manim from backend directory to avoid path issues
            backend_dir = Path(__file__).parent.parent.parent
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(backend_dir),
            )

            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                return {
                    "success": False,
                    "error": error_msg,
                    "message": f"Manim rendering failed: {error_msg}",
                    "script_path": str(script_path),
                }

            # Find the output video
            video_path = self._find_output_video(session_id)

            if not video_path:
                return {
                    "success": False,
                    "error": "Video file not found after rendering",
                    "message": "Rendering completed but video file not found",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }

            background_track = None
            background_music_error = None
            music_result = self._apply_background_music(video_path)
            if music_result.get("success"):
                video_path = Path(music_result["video_path"])
                background_track = music_result.get("track")
            else:
                background_music_error = music_result.get("error")

            video_url = f"/videos/{video_path.name}"

            return {
                "success": True,
                "video_path": str(video_path),
                "video_url": video_url,
                "session_id": session_id,
                "script_path": str(script_path),
                "background_track": background_track,
                "background_music_error": background_music_error,
                "message": "Animation rendered successfully",
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Rendering timeout (exceeded 5 minutes)",
                "message": "Animation rendering took too long",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error rendering animation: {str(e)}",
            }

    def _sanitize_manim_code(self, code: str) -> str:
        """
        Normalize generated Manim code to avoid known runtime errors.

        Currently this targets FadeIn calls that pass multiple mobjects directly,
        replacing them with a single VGroup argument.
        """
        if not code:
            return code
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code

        line_offsets = self._compute_line_offsets(code)
        replacements: List[tuple[int, int, str]] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            # Handle both FadeIn(...) and manimlib.animation.fading.FadeIn(...)
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
        Replace axes.get_axis_labels(x_label="x", y_label="y") with manual label creation.
        ManimGL's get_axis_labels() doesn't accept x_label/y_label keyword arguments.
        """
        import re

        # Pattern to find get_axis_labels with keyword arguments
        pattern = r'(\w+)\.get_axis_labels\s*\(\s*x_label\s*=\s*(["\'])([^"\']*)\2\s*,\s*y_label\s*=\s*(["\'])([^"\']*)\4\s*\)'

        def replace_labels(match):
            axes_var = match.group(1)
            x_text = match.group(3)
            y_text = match.group(5)

            # Generate replacement code that creates labels manually
            replacement = (
                f"VGroup("
                f'Tex("{x_text}").next_to({axes_var}.x_axis, DOWN), '
                f'Tex("{y_text}").next_to({axes_var}.y_axis, LEFT)'
                f")"
            )
            return replacement

        sanitized = re.sub(pattern, replace_labels, code)
        return sanitized

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
        # Common patterns for output videos
        patterns = [
            f"animation_{session_id}.mp4",
            f"animation_{session_id}.mov",
            f"scene_{session_id}.mp4",
            f"MathAnimation.mp4",
        ]

        # Search in temp directory and subdirectories
        for pattern in patterns:
            for video_file in self.temp_dir.rglob(pattern):
                return video_file

        # If not found with specific name, get the most recent mp4
        video_files = list(self.temp_dir.rglob("*.mp4"))
        if video_files:
            # Sort by modification time, return most recent
            video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return video_files[0]

        return None

    def _get_next_audio_track(self) -> Optional[Path]:
        if not self.background_music_enabled or not self.audio_tracks:
            return None
        with self._audio_lock:
            if not self.audio_tracks:
                return None
            track = self.audio_tracks[self._audio_index]
            self._audio_index = (self._audio_index + 1) % len(self.audio_tracks)
        return track

    def _apply_background_music(self, video_path: Path) -> dict:
        track = self._get_next_audio_track()
        if not track:
            return {
                "success": False,
                "video_path": str(video_path),
                "error": "Background music disabled or unavailable",
            }

        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=video_path.suffix, dir=str(video_path.parent)
        )
        temp_output = Path(temp_file.name)
        temp_file.close()

        video_duration = self._get_media_duration(video_path)
        if video_duration is None or video_duration <= 0:
            if temp_output.exists():
                try:
                    temp_output.unlink()
                except OSError:
                    pass
            return {"success": False, "video_path": str(video_path)}

        filter_complex = (
            f"[1:a]aloop=loop=-1:size=0:start=0,atrim=0:{video_duration:.3f},"
            f"asetpts=PTS-STARTPTS,volume={self.music_volume}[bgm]"
        )

        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(track),
                "-filter_complex",
                filter_complex,
                "-map",
                "0:v",
                "-map",
                "[bgm]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(temp_output),
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            os.replace(temp_output, video_path)
            return {
                "success": True,
                "video_path": str(video_path),
                "track": str(track),
            }
        except subprocess.CalledProcessError as e:
            if temp_output.exists():
                try:
                    temp_output.unlink()
                except OSError:
                    pass
            return {
                "success": False,
                "error": e.stderr or e.stdout,
                "video_path": str(video_path),
            }
        except Exception as e:
            if temp_output.exists():
                try:
                    temp_output.unlink()
                except OSError:
                    pass
            return {"success": False, "error": str(e), "video_path": str(video_path)}

    def _get_media_duration(self, media_path: Path) -> Optional[float]:
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(media_path),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration_str = result.stdout.strip()
            if not duration_str:
                return None
            duration = float(duration_str)
            if math.isnan(duration) or duration <= 0:
                return None
            return duration
        except (subprocess.CalledProcessError, ValueError):
            return None
        except Exception:
            return None

    def validate_code(self, code: str) -> dict:
        """
        Validate Manim code without rendering

        Args:
            code: Python code to validate

        Returns:
            dict with validation results
        """
        try:
            # Basic syntax check
            compile(code, "<string>", "exec")

            # Check for required imports
            has_import = "from manimlib" in code or "import manimlib" in code
            has_scene = "class" in code and "(Scene)" in code
            has_construct = "def construct(self)" in code

            issues = []
            if not has_import:
                issues.append("Missing 'from manimlib import *' or similar import")
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
