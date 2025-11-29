# -*- coding: utf-8 -*-
from manim import *

config.background_color = "#0f172a"

class GaussianElimination(Scene):
    def construct(self):
        # Title
        title = Text("Giải hệ phương trình tuyến tính bằng phương pháp Gauss", font_size=36, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)
        
        # Original Equations
        eq_intro_text = Text("Hệ phương trình:", font_size=30, color=WHITE)
        eq_intro_text.next_to(title, DOWN, buff=0.7)

        eq1 = MathTex("x+y+z=9", font_size=40)
        eq2 = MathTex("2x+5y+7z=52", font_size=40)
        eq3 = MathTex("2x+y-z=0", font_size=40)
        
        equations_group = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.3)
        equations_group.move_to(ORIGIN).shift(UP * 0.5) # Center and shift up slightly
        
        self.play(Write(eq_intro_text), Create(equations_group))
        self.wait(2)
        
        # Transition to Augmented Matrix
        matrix_intro_text = Text("Ma trận mở rộng:", font_size=30, color=WHITE)
        matrix_intro_text.next_to(eq_intro_text, DOWN, buff=0.7)
        matrix_intro_text.shift(DOWN * 0.5) # Make space
        
        initial_matrix_values = [[1, 1, 1, 9],
                                 [2, 5, 7, 52],
                                 [2, 1, -1, 0]]
        
        matrix = Matrix(initial_matrix_values, h_buff=1.5, v_buff=0.8, include_background_rectangle=True)
        matrix.scale(0.7)
        matrix.move_to(ORIGIN).shift(DOWN * 0.5) # Position below equations
        
        self.play(FadeOut(equations_group, shift=UP), 
                  Transform(eq_intro_text, matrix_intro_text)) # Transform equation label to matrix label
        self.play(Create(matrix))
        self.wait(1.5)
        
        # --- Gaussian Elimination Steps ---
        
        # R2 -> R2 - 2*R1
        op1_text = MathTex("R_2 \\to R_2 - 2R_1", font_size=35).to_edge(LEFT, buff=0.5).shift(UP*0.5)
        self.play(Write(op1_text))
        self.play(matrix.get_rows()[0].animate.set_color(BLUE), matrix.get_rows()[1].animate.set_color(YELLOW))
        self.wait(1)
        
        matrix2 = Matrix([[1, 1, 1, 9],
                          [0, 3, 5, 34], # 2-2*1=0, 5-2*1=3, 7-2*1=5, 52-2*9=34
                          [2, 1, -1, 0]], h_buff=1.5, v_buff=0.8, include_background_rectangle=True)
        matrix2.scale(0.7).move_to(matrix.get_center())
        
        self.play(Transform(matrix, matrix2), FadeOut(op1_text))
        self.play(matrix.get_rows()[0].animate.set_color(WHITE), matrix.get_rows()[1].animate.set_color(WHITE))
        self.wait(1.5)
        
        # R3 -> R3 - 2*R1
        op2_text = MathTex("R_3 \\to R_3 - 2R_1", font_size=35).to_edge(LEFT, buff=0.5).shift(UP*0.5)
        self.play(Write(op2_text))
        self.play(matrix.get_rows()[0].animate.set_color(BLUE), matrix.get_rows()[2].animate.set_color(YELLOW))
        self.wait(1)
        
        matrix3 = Matrix([[1, 1, 1, 9],
                          [0, 3, 5, 34],
                          [0, -1, -3, -18]], h_buff=1.5, v_buff=0.8, include_background_rectangle=True) # 2-2*1=0, 1-2*1=-1, -1-2*1=-3, 0-2*9=-18
        matrix3.scale(0.7).move_to(matrix.get_center())
        
        self.play(Transform(matrix, matrix3), FadeOut(op2_text))
        self.play(matrix.get_rows()[0].animate.set_color(WHITE), matrix.get_rows()[2].animate.set_color(WHITE))
        self.wait(1.5)
        
        # R2 <-> R3 (swap to make pivot 1)
        op3_text = MathTex("R_2 \\leftrightarrow R_3", font_size=35).to_edge(LEFT, buff=0.5).shift(UP*0.5)
        self.play(Write(op3_text))
        self.play(matrix.get_rows()[1].animate.set_color(YELLOW), matrix.get_rows()[2].animate.set_color(YELLOW))
        self.wait(1)

        matrix4 = Matrix([[1, 1, 1, 9],
                          [0, -1, -3, -18],
                          [0, 3, 5, 34]], h_buff=1.5, v_buff=0.8, include_background_rectangle=True)
        matrix4.scale(0.7).move_to(matrix.get_center())
        
        self.play(Transform(matrix, matrix4), FadeOut(op3_text))
        self.play(matrix.get_rows()[1].animate.set_color(WHITE), matrix.get_rows()[2].animate.set_color(WHITE))
        self.wait(1.5)

        # R2 -> -R2
        op4_text = MathTex("R_2 \\to -R_2", font_size=35).to_edge(LEFT, buff=0.5).shift(UP*0.5)
        self.play(Write(op4_text))
        self.play(matrix.get_rows()[1].animate.set_color(BLUE))
        self.wait(1)
        
        matrix5 = Matrix([[1, 1, 1, 9],
                          [0, 1, 3, 18], # 0*-1=0, -1*-1=1, -3*-1=3, -18*-1=18
                          [0, 3, 5, 34]], h_buff=1.5, v_buff=0.8, include_background_rectangle=True)
        matrix5.scale(0.7).move_to(matrix.get_center())
        
        self.play(Transform(matrix, matrix5), FadeOut(op4_text))
        self.play(matrix.get_rows()[1].animate.set_color(WHITE))
        self.wait(1.5)
        
        # R3 -> R3 - 3*R2
        op5_text = MathTex("R_3 \\to R_3 - 3R_2", font_size=35).to_edge(LEFT, buff=0.5).shift(UP*0.5)
        self.play(Write(op5_text))
        self.play(matrix.get_rows()[1].animate.set_color(BLUE), matrix.get_rows()[2].animate.set_color(YELLOW))
        self.wait(1)
        
        matrix6 = Matrix([[1, 1, 1, 9],
                          [0, 1, 3, 18],
                          [0, 0, -4, -20]], h_buff=1.5, v_buff=0.8, include_background_rectangle=True) # 0-3*0=0, 3-3*1=0, 5-3*3=-4, 34-3*18=-20
        matrix6.scale(0.7).move_to(matrix.get_center())
        
        self.play(Transform(matrix, matrix6), FadeOut(op5_text))
        self.play(matrix.get_rows()[1].animate.set_color(WHITE), matrix.get_rows()[2].animate.set_color(WHITE))
        self.wait(1.5)
        
        # R3 -> (-1/4)*R3
        op6_text = MathTex("R_3 \\to -\\frac{1}{4}R_3", font_size=35).to_edge(LEFT, buff=0.5).shift(UP*0.5)
        self.play(Write(op6_text))
        self.play(matrix.get_rows()[2].animate.set_color(BLUE))
        self.wait(1)
        
        matrix7 = Matrix([[1, 1, 1, 9],
                          [0, 1, 3, 18],
                          [0, 0, 1, 5]], h_buff=1.5, v_buff=0.8, include_background_rectangle=True) # 0*-1/4=0, 0*-1/4=0, -4*-1/4=1, -20*-1/4=5
        matrix7.scale(0.7).move_to(matrix.get_center())
        
        self.play(Transform(matrix, matrix7), FadeOut(op6_text))
        self.play(matrix.get_rows()[2].animate.set_color(WHITE))
        self.wait(2)
        
        # --- Back Substitution ---
        self.play(FadeOut(matrix, shift=DOWN), FadeOut(eq_intro_text, shift=DOWN)) # Fade out the matrix and its label
        
        final_eq_intro_text = Text("Hệ phương trình tương đương:", font_size=30, color=WHITE).to_edge(UP, buff=0.5)
        
        # Use copies of the original equation MathTex objects to highlight
        final_eq1 = MathTex("x+y+z=9", font_size=40)
        final_eq2 = MathTex("y+3z=18", font_size=40)
        final_eq3 = MathTex("z=5", font_size=40)
        
        final_equations_group = VGroup(final_eq1, final_eq2, final_eq3).arrange(DOWN, buff=0.3)
        final_equations_group.move_to(ORIGIN).shift(UP * 0.5) # Center on screen!
        
        self.play(Transform(title, final_eq_intro_text)) # Transform original title to new label
        self.play(Write(final_equations_group))
        self.wait(1.5)
        
        # Solve for z
        solve_z_result = MathTex("z = 5", font_size=45, color=GREEN)
        solve_z_result.next_to(final_equations_group, DOWN, buff=1.0)
        self.play(final_eq3.animate.set_color(YELLOW))
        self.play(Transform(final_eq3.copy(), solve_z_result)) # Animate from a copy of eq3
        self.play(final_eq3.animate.set_color(WHITE)) # Revert color
        self.wait(1.5)
        
        # Solve for y
        solve_y_interim = MathTex("y + 3(5) = 18", font_size=45)
        solve_y_result = MathTex("y = 3", font_size=45, color=GREEN)
        
        solve_y_interim.next_to(solve_z_result, DOWN, buff=0.7)
        self.play(final_eq2.animate.set_color(YELLOW))
        self.play(Write(solve_y_interim))
        self.wait(1)
        self.play(Transform(solve_y_interim, solve_y_result)) # solve_y_interim becomes solve_y_result
        self.play(final_eq2.animate.set_color(WHITE)) # Revert color
        self.wait(1.5)
        
        # Solve for x
        solve_x_interim = MathTex("x + 3 + 5 = 9", font_size=45)
        solve_x_result = MathTex("x = 1", font_size=45, color=GREEN)
        
        solve_x_interim.next_to(solve_y_interim, DOWN, buff=0.7) # Position below the transformed y result
        self.play(final_eq1.animate.set_color(YELLOW))
        self.play(Write(solve_x_interim))
        self.wait(1)
        self.play(Transform(solve_x_interim, solve_x_result)) # solve_x_interim becomes solve_x_result
        self.play(final_eq1.animate.set_color(WHITE))
        self.wait(1.5)
        
        # Final Answer
        final_answer_text = Text("Vậy, nghiệm của hệ là:", font_size=36, color=WHITE)
        answer_values = MathTex("x=1, y=3, z=5", font_size=45, color=GREEN)
        
        answer_group = VGroup(final_answer_text, answer_values).arrange(DOWN, buff=0.5)
        answer_group.move_to(ORIGIN).shift(DOWN * 1.5) # Reposition to fit
        
        # Clean up all previous elements
        self.play(FadeOut(title), # title is now final_eq_intro_text
                  FadeOut(final_equations_group), 
                  FadeOut(solve_z_result), 
                  FadeOut(solve_y_interim), # This is solve_y_result after transformation
                  FadeOut(solve_x_interim)) # This is solve_x_result after transformation
        
        self.play(Write(final_answer_text))
        self.play(Write(answer_values))
        self.wait(3)