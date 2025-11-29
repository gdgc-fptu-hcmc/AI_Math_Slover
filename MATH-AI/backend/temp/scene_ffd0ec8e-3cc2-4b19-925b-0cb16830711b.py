# -*- coding: utf-8 -*-
from manim import *

config.background_color = "#0f172a"

class GaussianElimination(Scene):
    def construct(self):
        # Title
        title = Text("Giải hệ phương trình tuyến tính", font_size=36, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)

        # Problem Statement
        problem_text = Text("Sử dụng phương pháp khử Gauss:", font_size=28, color=WHITE)
        problem_text.next_to(title, DOWN, buff=0.4)
        self.play(Write(problem_text))
        self.wait(1)

        # Equations
        eq1 = MathTex("x+y+z=9", font_size=36)
        eq2 = MathTex("2x+5y+7z=52", font_size=36)
        eq3 = MathTex("2x+y-z=0", font_size=36)

        eqs = VGroup(eq1, eq2, eq3)
        eqs.arrange(DOWN, buff=0.3)
        eqs.move_to(ORIGIN).shift(UP * 0.5) # Shift up to make space for matrix later

        self.play(Write(eqs))
        self.wait(2)

        # Convert to Augmented Matrix
        matrix_intro = Text("Ma trận mở rộng:", font_size=28, color=WHITE)
        matrix_intro.next_to(eqs, DOWN, buff=0.8)

        initial_matrix_elements = [[1, 1, 1, "|", 9],
                                   [2, 5, 7, "|", 52],
                                   [2, 1, -1, "|", 0]]
        initial_matrix = Matrix(initial_matrix_elements, h_buff=1.5, v_buff=0.8)
        initial_matrix.scale(0.7) # Scale to fit
        initial_matrix.next_to(matrix_intro, DOWN, buff=0.5)

        self.play(Write(matrix_intro), Create(initial_matrix))
        self.wait(2)

        # Clear initial equations and intro text, move matrix up for operations
        self.play(FadeOut(eqs), FadeOut(matrix_intro))
        self.play(initial_matrix.animate.move_to(UP * 1.5))
        self.wait(1)

        current_matrix = initial_matrix
        # --- Gaussian Elimination Steps ---

        # Step 1: R2 <- R2 - 2R1
        op1_text = MathTex("R_2 \\leftarrow R_2 - 2R_1", font_size=32, color=BLUE)
        op1_text.to_edge(DOWN, buff=0.5)
        self.play(Write(op1_text))
        self.wait(1)

        matrix1_elements = [[1, 1, 1, "|", 9],
                            [0, 3, 5, "|", 34],
                            [2, 1, -1, "|", 0]]
        matrix1 = Matrix(matrix1_elements, h_buff=1.5, v_buff=0.8).scale(0.7)
        matrix1.move_to(current_matrix.get_center())

        self.play(Transform(current_matrix, matrix1))
        self.wait(2)

        # Step 2: R3 <- R3 - 2R1
        op2_text = MathTex("R_3 \\leftarrow R_3 - 2R_1", font_size=32, color=BLUE)
        # Overwrite previous operation text
        self.play(ReplacementTransform(op1_text, op2_text))
        self.wait(1)

        matrix2_elements = [[1, 1, 1, "|", 9],
                            [0, 3, 5, "|", 34],
                            [0, -1, -3, "|", -18]]
        matrix2 = Matrix(matrix2_elements, h_buff=1.5, v_buff=0.8).scale(0.7)
        matrix2.move_to(current_matrix.get_center())

        self.play(Transform(current_matrix, matrix2))
        self.wait(2)

        # Step 3: Swap R2 and R3 to get a leading 1
        op3_text = MathTex("R_2 \\leftrightarrow R_3", font_size=32, color=BLUE)
        self.play(ReplacementTransform(op2_text, op3_text))
        self.wait(1)

        matrix3_elements = [[1, 1, 1, "|", 9],
                            [0, -1, -3, "|", -18],
                            [0, 3, 5, "|", 34]]
        matrix3 = Matrix(matrix3_elements, h_buff=1.5, v_buff=0.8).scale(0.7)
        matrix3.move_to(current_matrix.get_center())

        self.play(Transform(current_matrix, matrix3))
        self.wait(2)

        # Step 4: R2 <- -R2 to make leading coefficient 1
        op4_text = MathTex("R_2 \\leftarrow -R_2", font_size=32, color=BLUE)
        self.play(ReplacementTransform(op3_text, op4_text))
        self.wait(1)

        matrix4_elements = [[1, 1, 1, "|", 9],
                            [0, 1, 3, "|", 18],
                            [0, 3, 5, "|", 34]]
        matrix4 = Matrix(matrix4_elements, h_buff=1.5, v_buff=0.8).scale(0.7)
        matrix4.move_to(current_matrix.get_center())

        self.play(Transform(current_matrix, matrix4))
        self.wait(2)

        # Step 5: R3 <- R3 - 3R2
        op5_text = MathTex("R_3 \\leftarrow R_3 - 3R_2", font_size=32, color=BLUE)
        self.play(ReplacementTransform(op4_text, op5_text))
        self.wait(1)

        matrix5_elements = [[1, 1, 1, "|", 9],
                            [0, 1, 3, "|", 18],
                            [0, 0, -4, "|", -20]]
        matrix5 = Matrix(matrix5_elements, h_buff=1.5, v_buff=0.8).scale(0.7)
        matrix5.move_to(current_matrix.get_center())

        self.play(Transform(current_matrix, matrix5))
        self.wait(2)

        # Step 6: R3 <- (-1/4)R3 to make leading coefficient 1
        op6_text = MathTex("R_3 \\leftarrow -\\frac{1}{4}R_3", font_size=32, color=BLUE)
        self.play(ReplacementTransform(op5_text, op6_text))
        self.wait(1)

        final_matrix_elements = [[1, 1, 1, "|", 9],
                                 [0, 1, 3, "|", 18],
                                 [0, 0, 1, "|", 5]]
        final_matrix = Matrix(final_matrix_elements, h_buff=1.5, v_buff=0.8).scale(0.7)
        final_matrix.move_to(current_matrix.get_center())

        self.play(Transform(current_matrix, final_matrix))
        self.wait(2)

        self.play(FadeOut(op6_text))
        self.wait(1)

        # Back Substitution / Solution
        solution_intro = Text("Từ ma trận bậc thang rút gọn:", font_size=28, color=WHITE)
        solution_intro.next_to(current_matrix, DOWN, buff=0.8)
        self.play(Write(solution_intro))
        self.wait(1)

        sol_z_eq = MathTex("z = 5", font_size=36, color=GREEN)
        sol_y_eq = MathTex("y + 3z = 18", font_size=36)
        sol_x_eq = MathTex("x + y + z = 9", font_size=36)

        sol_eqs_group = VGroup(sol_x_eq, sol_y_eq, sol_z_eq)
        sol_eqs_group.arrange(DOWN, buff=0.3)
        sol_eqs_group.next_to(solution_intro, DOWN, buff=0.5)

        self.play(Write(sol_eqs_group[2])) # z = 5
        self.wait(1)
        self.play(Write(sol_eqs_group[1])) # y + 3z = 18
        self.wait(1)

        sol_y_val = MathTex("y + 3(5) = 18 \\Rightarrow y = 3", font_size=36, color=GREEN)
        sol_y_val.move_to(sol_eqs_group[1].get_center())
        self.play(Transform(sol_eqs_group[1], sol_y_val))
        self.wait(1)

        self.play(Write(sol_eqs_group[0])) # x + y + z = 9
        self.wait(1)

        sol_x_val = MathTex("x + 3 + 5 = 9 \\Rightarrow x = 1", font_size=36, color=GREEN)
        sol_x_val.move_to(sol_eqs_group[0].get_center())
        self.play(Transform(sol_eqs_group[0], sol_x_val))
        self.wait(2)

        # Final Answer
        final_answer_text = Text("Vậy, nghiệm của hệ phương trình là:", font_size=32, color=YELLOW)
        final_answer_text.next_to(sol_eqs_group, DOWN, buff=0.8)

        final_solution = MathTex("x=1, y=3, z=5", font_size=48, color=GREEN)
        final_solution.next_to(final_answer_text, DOWN, buff=0.4)

        # Clear previous elements and display final solution centrally
        self.play(FadeOut(current_matrix), FadeOut(solution_intro), FadeOut(title), 
                  FadeOut(problem_text), FadeOut(sol_eqs_group))
        
        final_solution_group = VGroup(final_answer_text, final_solution)
        final_solution_group.arrange(DOWN, buff=0.5).move_to(ORIGIN)

        self.play(Write(final_answer_text))
        self.play(Write(final_solution))
        self.wait(3)