from manim import *

config.background_color = "#0f172a"

class MathAnimation(Scene):
    def construct(self):
        # Title (Vietnamese with Text, no font)
        title = Text("Giải hệ phương trình tuyến tính", font_size=40, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(2)

        # Problem Statement (Vietnamese label with Text, math with MathTex)
        problem_label = Text("Hệ phương trình:", font_size=32).next_to(title, DOWN, buff=0.8)
        self.play(Write(problem_label))
        self.wait(1)

        system_eq = MathTex(
            r"\begin{cases} x+y+z=9 \\ 2x+5y+7z=52 \\ 2x+y-z=0 \end{cases}",
            font_size=48
        ).next_to(problem_label, DOWN, buff=0.5)
        self.play(Write(system_eq))
        self.wait(3)

        # Convert to Augmented Matrix (Vietnamese label with Text, matrix with MathTex)
        matrix_label = Text("Ma trận mở rộng:", font_size=32).next_to(system_eq, DOWN, buff=0.8)
        self.play(FadeIn(matrix_label))
        self.wait(1)

        initial_matrix_tex = MathTex(
            r"\begin{bmatrix} 1 & 1 & 1 & | & 9 \\ 2 & 5 & 7 & | & 52 \\ 2 & 1 & -1 & | & 0 \end{bmatrix}",
            font_size=48
        ).next_to(matrix_label, DOWN, buff=0.5).shift(LEFT * 0.5)
        self.play(Write(initial_matrix_tex))
        self.wait(3)

        # Store the current matrix for transformations
        current_matrix = initial_matrix_tex

        # --- Gaussian Elimination Steps ---

        # Step 1: R2 = R2 - 2R1, R3 = R3 - 2R1
        step1_label = Text("Bước 1: Biến đổi hàng 2 và 3", font_size=32, color=BLUE).to_edge(LEFT).shift(UP*1.5)
        r2_op = MathTex(r"R_2 \leftarrow R_2 - 2R_1", font_size=36).next_to(step1_label, DOWN, buff=0.5, aligned_edge=LEFT)
        r3_op = MathTex(r"R_3 \leftarrow R_3 - 2R_1", font_size=36).next_to(r2_op, DOWN, buff=0.2, aligned_edge=LEFT)
        
        self.play(FadeIn(step1_label), Write(r2_op), Write(r3_op))
        self.wait(2)

        # New matrix after operations
        matrix_step1_tex = MathTex(
            r"\begin{bmatrix} 1 & 1 & 1 & | & 9 \\ 0 & 3 & 5 & | & 34 \\ 0 & -1 & -3 & | & -18 \end{bmatrix}",
            font_size=48
        ).move_to(current_matrix)
        
        self.play(Transform(current_matrix, matrix_step1_tex))
        self.wait(3)
        self.play(FadeOut(r2_op), FadeOut(r3_op))

        # Step 2: R3 = R3 + (1/3)R2
        step2_label = Text("Bước 2: Biến đổi hàng 3", font_size=32, color=BLUE).to_edge(LEFT).shift(UP*1.5)
        r3_op_2 = MathTex(r"R_3 \leftarrow R_3 + \frac{1}{3}R_2", font_size=36).next_to(step2_label, DOWN, buff=0.5, aligned_edge=LEFT)

        self.play(FadeIn(step2_label), Write(r3_op_2))
        self.wait(2)

        # New matrix after operation (Row Echelon Form)
        matrix_step2_tex = MathTex(
            r"\begin{bmatrix} 1 & 1 & 1 & | & 9 \\ 0 & 3 & 5 & | & 34 \\ 0 & 0 & -\frac{4}{3} & | & -\frac{20}{3} \end{bmatrix}",
            font_size=48
        ).move_to(current_matrix)

        self.play(Transform(current_matrix, matrix_step2_tex))
        self.wait(3)
        self.play(FadeOut(r3_op_2))

        # --- Back Substitution ---
        back_sub_label = Text("Thay ngược để tìm nghiệm:", font_size=32, color=GREEN).to_edge(LEFT).shift(UP*1.5)
        self.play(FadeIn(back_sub_label))
        self.wait(2)
        
        # Scale and reposition the matrix for clarity
        self.play(current_matrix.animate.scale(0.8).next_to(back_sub_label, DOWN, buff=0.5).to_edge(LEFT))
        self.wait(1)

        # Solve for z
        eq_z = MathTex(r"-\frac{4}{3}z = -\frac{20}{3}", font_size=36).next_to(current_matrix, RIGHT, buff=1.0).shift(UP*1.0)
        sol_z = MathTex(r"z = 5", font_size=48, color=YELLOW).next_to(eq_z, DOWN, buff=0.5)
        self.play(Write(eq_z))
        self.wait(2)
        self.play(Write(sol_z))
        self.wait(2)

        # Solve for y
        eq_y = MathTex(r"3y + 5z = 34", font_size=36).next_to(sol_z, DOWN, buff=0.8).align_to(eq_z, LEFT)
        sub_y = MathTex(r"3y + 5(5) = 34", font_size=36).next_to(eq_y, DOWN, buff=0.2).align_to(eq_y, LEFT)
        sol_y = MathTex(r"3y = 9 \Rightarrow y = 3", font_size=48, color=YELLOW).next_to(sub_y, DOWN, buff=0.5)
        self.play(Write(eq_y))
        self.wait(2)
        self.play(Write(sub_y))
        self.wait(2)
        self.play(Write(sol_y))
        self.wait(2)

        # Solve for x
        eq_x = MathTex(r"x + y + z = 9", font_size=36).next_to(sol_y, DOWN, buff=0.8).align_to(eq_z, LEFT)
        sub_x = MathTex(r"x + 3 + 5 = 9", font_size=36).next_to(eq_x, DOWN, buff=0.2).align_to(eq_x, LEFT)
        sol_x = MathTex(r"x + 8 = 9 \Rightarrow x = 1", font_size=48, color=YELLOW).next_to(sub_x, DOWN, buff=0.5)
        self.play(Write(eq_x))
        self.wait(2)
        self.play(Write(sub_x))
        self.wait(2)
        self.play(Write(sol_x))
        self.wait(2)

        # Final Answer
        self.play(FadeOut(current_matrix), FadeOut(eq_z), FadeOut(sol_z), FadeOut(eq_y), FadeOut(sub_y), FadeOut(sol_y), FadeOut(eq_x), FadeOut(sub_x), FadeOut(sol_x), FadeOut(back_sub_label), FadeOut(step1_label), FadeOut(step2_label))
        self.wait(1)
        
        answer_label = Text("Nghiệm của hệ phương trình:", font_size=36, color=GREEN).to_edge(UP).shift(DOWN*0.5)
        final_answer = MathTex(
            r"x=1, \quad y=3, \quad z=5",
            font_size=64, color=YELLOW
        ).next_to(answer_label, DOWN, buff=1)
        
        self.play(Write(answer_label))
        self.wait(1)
        self.play(Write(final_answer))
        self.wait(4)