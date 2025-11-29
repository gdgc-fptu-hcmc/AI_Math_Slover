# -*- coding: utf-8 -*-
from manim import *

config.background_color = "#0f172a"

class GaussianElimination(Scene):
    def construct(self):
        # Title - NO FONT PARAMETER!
        title = Text("Giải hệ phương trình tuyến tính bằng phương pháp Gauss", font_size=36, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)
        
        # Equations - center them properly
        eq1 = MathTex("x + y + z = 9", font_size=40, color=WHITE)
        eq2 = MathTex("2x + 5y + 7z = 52", font_size=40, color=WHITE)
        eq3 = MathTex("2x + y - z = 0", font_size=40, color=WHITE)
        
        eqs = VGroup(eq1, eq2, eq3)
        eqs.arrange(DOWN, buff=0.3)
        eqs.move_to(ORIGIN).shift(UP * 1.5) # Center on screen and shift up
        
        self.play(Write(eqs))
        self.wait(2)
        
        # Initial Augmented Matrix - scale to fit
        initial_matrix_data = [[1, 1, 1, 9],
                               [2, 5, 7, 52],
                               [2, 1, -1, 0]]
        
        # Create the augmented matrix with a vertical line
        matrix = Matrix(initial_matrix_data, h_buff=1.5, v_buff=0.8, left_bracket="[", right_bracket="]")
        matrix.add_columns([Tex('|')], col_widths=[0.1], x_labels=[3]) # Insert line after 3rd column (0-indexed)
        matrix.scale(0.75)  # Prevent overflow
        matrix.next_to(eqs, DOWN, buff=0.8)
        
        self.play(Create(matrix))
        self.wait(2)
        
        # --- Gaussian Elimination Steps ---

        # Operation 1: R2 -> R2 - 2R1
        operation1_text = MathTex("R_2 \\to R_2 - 2R_1", font_size=32, color=BLUE)
        operation1_text.next_to(matrix, DOWN, buff=0.5)
        self.play(Write(operation1_text))
        self.wait(1)

        matrix_step1_data = [[1, 1, 1, 9],
                             [0, 3, 5, 34], # (2-2*1), (5-2*1), (7-2*1), (52-2*9)
                             [2, 1, -1, 0]]
        
        matrix_step1 = Matrix(matrix_step1_data, h_buff=1.5, v_buff=0.8, left_bracket="[", right_bracket="]")
        matrix_step1.add_columns([Tex('|')], col_widths=[0.1], x_labels=[3])
        matrix_step1.scale(0.75)
        matrix_step1.move_to(matrix) # Position new matrix exactly on top of old one
        
        self.play(Transform(matrix, matrix_step1))
        self.remove(operation1_text) # Remove old operation text
        self.wait(1.5)

        # Operation 2: R3 -> R3 - 2R1
        operation2_text = MathTex("R_3 \\to R_3 - 2R_1", font_size=32, color=BLUE)
        operation2_text.next_to(matrix, DOWN, buff=0.5)
        self.play(Write(operation2_text))
        self.wait(1)

        matrix_step2_data = [[1, 1, 1, 9],
                             [0, 3, 5, 34],
                             [0, -1, -3, -18]] # (2-2*1), (1-2*1), (-1-2*1), (0-2*9)
        
        matrix_step2 = Matrix(matrix_step2_data, h_buff=1.5, v_buff=0.8, left_bracket="[", right_bracket="]")
        matrix_step2.add_columns([Tex('|')], col_widths=[0.1], x_labels=[3])
        matrix_step2.scale(0.75)
        matrix_step2.move_to(matrix)
        
        self.play(Transform(matrix, matrix_step2))
        self.remove(operation2_text)
        self.wait(1.5)
        
        # Operation 3: R3 -> 3R3 + R2
        operation3_text = MathTex("R_3 \\to 3R_3 + R_2", font_size=32, color=BLUE)
        operation3_text.next_to(matrix, DOWN, buff=0.5)
        self.play(Write(operation3_text))
        self.wait(1)

        matrix_step3_data = [[1, 1, 1, 9],
                             [0, 3, 5, 34],
                             [0, 0, -4, -20]] # (3*0+0), (3*-1+3), (3*-3+5), (3*-18+34)
        
        matrix_step3 = Matrix(matrix_step3_data, h_buff=1.5, v_buff=0.8, left_bracket="[", right_bracket="]")
        matrix_step3.add_columns([Tex('|')], col_widths=[0.1], x_labels=[3])
        matrix_step3.scale(0.75)
        matrix_step3.move_to(matrix)
        
        self.play(Transform(matrix, matrix_step3))
        self.remove(operation3_text)
        self.wait(2)

        # Fade out equations and move matrix up for solution
        self.play(FadeOut(eqs, shift=UP), matrix.animate.shift(UP * 1.5))
        self.wait(1)

        # Back-substitution and Solution
        solution_title = Text("Giải bằng phương pháp thế ngược:", font_size=32, color=YELLOW)
        solution_title.next_to(matrix, DOWN, buff=0.8)
        self.play(Write(solution_title))
        self.wait(1)

        # Z solution
        solution_eq_z = MathTex("-4z = -20 \\implies z = 5", font_size=36, color=GREEN)
        solution_eq_z.next_to(solution_title, DOWN, buff=0.5)
        self.play(Write(solution_eq_z))
        self.wait(1.5)

        # Y solution
        solution_eq_y = MathTex("3y + 5z = 34 \\implies 3y + 5(5) = 34 \\implies 3y = 9 \\implies y = 3", font_size=36, color=GREEN)
        solution_eq_y.next_to(solution_eq_z, DOWN, buff=0.5)
        self.play(Write(solution_eq_y))
        self.wait(1.5)

        # X solution
        solution_eq_x = MathTex("x + y + z = 9 \\implies x + 3 + 5 = 9 \\implies x + 8 = 9 \\implies x = 1", font_size=36, color=GREEN)
        solution_eq_x.next_to(solution_eq_y, DOWN, buff=0.5)
        self.play(Write(solution_eq_x))
        self.wait(2)
        
        # Final answer - keep away from edge
        final_answer = Text("Đáp án: x=1, y=3, z=5", font_size=48, color=YELLOW)
        final_answer.next_to(solution_eq_x, DOWN, buff=0.8)
        self.play(Write(final_answer))
        self.wait(3)