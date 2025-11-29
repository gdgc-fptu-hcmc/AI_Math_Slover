# -*- coding: utf-8 -*-
from manim import *

config.background_color = "#0f172a"

class GaussianElimination(Scene):
    def construct(self):
        # Title
        title = Text("Giải hệ phương trình bằng khử Gauss", font_size=36, color=YELLOW)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(1)
        
        # Initial System of Equations
        eq1_str = "x+y+z=9"
        eq2_str = "2x+5y+7z=52"
        eq3_str = "2x+y-z=0"
        
        eq1 = MathTex(eq1_str, font_size=40, color=WHITE)
        eq2 = MathTex(eq2_str, font_size=40, color=WHITE)
        eq3 = MathTex(eq3_str, font_size=40, color=WHITE)
        
        equations = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.3)
        equations.move_to(ORIGIN)
        
        self.play(Write(equations))
        self.wait(2)
        
        # Introduce Augmented Matrix
        matrix_intro = Text("Chuyển đổi sang ma trận mở rộng:", font_size=30, color=BLUE)
        matrix_intro.next_to(equations, DOWN, buff=0.8)
        self.play(Write(matrix_intro))
        self.wait(1)

        # Initial Augmented Matrix
        matrix_data_1 = [[1, 1, 1, 9],
                         [2, 5, 7, 52],
                         [2, 1, -1, 0]]
        
        matrix1 = Matrix(matrix_data_1, v_buff=0.8, h_buff=1.5, bracket_h_buff=SMALL_BUFF)
        
        # Calculate x-coordinate for the vertical augmented line
        # It should be between the 3rd and 4th column entries
        # matrix1.get_entries()[0][2] is the Mobject for the '1' in the first row (3rd column)
        # matrix1.get_entries()[0][3] is the Mobject for the '9' in the first row (4th column)
        x_coord_line = (matrix1.get_entries()[0][2].get_right()[0] + matrix1.get_entries()[0][3].get_left()[0]) / 2
        
        # Determine the height and vertical position for the line
        line_height = matrix1.get_brackets().height * 0.9 
        line_y_center = matrix1.get_brackets().get_center()[1]
        
        augmented_line = Line(
            [x_coord_line, line_y_center + line_height/2, 0],
            [x_coord_line, line_y_center - line_height/2, 0]
        )
        augmented_line.set_color(WHITE)

        matrix_group1 = VGroup(matrix1, augmented_line)
        matrix_group1.scale(0.8)
        matrix_group1.move_to(ORIGIN)
        
        self.play(FadeOut(equations, matrix_intro, shift=UP)) 
        self.play(Create(matrix_group1))
        self.wait(2)
        
        current_matrix_group = matrix_group1 # Keep track of the current matrix state

        operation_text1 = Text("Thực hiện: R2 ← R2 - 2R1", font_size=32, color=BLUE).to_edge(UP, buff=0.5)
        self.play(Transform(title, operation_text1))
        
        # Highlight R1 and R2
        r1_rect = SurroundingRectangle(current_matrix_group[0].get_rows()[0], color=RED, buff=0.1)
        r2_rect = SurroundingRectangle(current_matrix_group[0].get_rows()[1], color=RED, buff=0.1)
        self.play(Create(r1_rect), Create(r2_rect))
        self.wait(1)
        
        matrix_data_2 = [[1, 1, 1, 9],
                         [0, 3, 5, 34], # R2 - 2R1 = [2-2*1, 5-2*1, 7-2*1, 52-2*9] = [0, 3, 5, 34]
                         [2, 1, -1, 0]]
        
        matrix2 = Matrix(matrix_data_2, v_buff=0.8, h_buff=1.5, bracket_h_buff=SMALL_BUFF)
        augmented_line2 = augmented_line.copy() 
        matrix_group2 = VGroup(matrix2, augmented_line2).scale(0.8).move_to(current_matrix_group.get_center())

        self.play(Transform(current_matrix_group, matrix_group2), FadeOut(r1_rect, r2_rect))
        self.wait(2)
        current_matrix_group = matrix_group2

        operation_text2 = Text("Thực hiện: R3 ← R3 - 2R1", font_size=32, color=BLUE).to_edge(UP, buff=0.5)
        self.play(Transform(title, operation_text2))

        # Highlight R1 and R3
        r1_rect = SurroundingRectangle(current_matrix_group[0].get_rows()[0], color=RED, buff=0.1)
        r3_rect = SurroundingRectangle(current_matrix_group[0].get_rows()[2], color=RED, buff=0.1)
        self.play(Create(r1_rect), Create(r3_rect))
        self.wait(1)
        
        matrix_data_3 = [[1, 1, 1, 9],
                         [0, 3, 5, 34],
                         [0, -1, -3, -18]] # R3 - 2R1 = [2-2*1, 1-2*1, -1-2*1, 0-2*9] = [0, -1, -3, -18]

        matrix3 = Matrix(matrix_data_3, v_buff=0.8, h_buff=1.5, bracket_h_buff=SMALL_BUFF)
        augmented_line3 = augmented_line.copy()
        matrix_group3 = VGroup(matrix3, augmented_line3).scale(0.8).move_to(current_matrix_group.get_center())

        self.play(Transform(current_matrix_group, matrix_group3), FadeOut(r1_rect, r3_rect))
        self.wait(2)
        current_matrix_group = matrix_group3

        operation_text3 = Text("Thực hiện: R3 ← 3R3 + R2", font_size=32, color=BLUE).to_edge(UP, buff=0.5)
        self.play(Transform(title, operation_text3))

        # Highlight R2 and R3
        r2_rect = SurroundingRectangle(current_matrix_group[0].get_rows()[1], color=RED, buff=0.1)
        r3_rect = SurroundingRectangle(current_matrix_group[0].get_rows()[2], color=RED, buff=0.1)
        self.play(Create(r2_rect), Create(r3_rect))
        self.wait(1)

        matrix_data_4 = [[1, 1, 1, 9],
                         [0, 3, 5, 34],
                         [0, 0, -4, -20]] # 3*R3 + R2 = [3*0+0, 3*(-1)+3, 3*(-3)+5, 3*(-18)+34] = [0, 0, -4, -20]
        
        matrix4 = Matrix(matrix_data_4, v_buff=0.8, h_buff=1.5, bracket_h_buff=SMALL_BUFF)
        augmented_line4 = augmented_line.copy()
        matrix_group4 = VGroup(matrix4, augmented_line4).scale(0.8).move_to(current_matrix_group.get_center())

        self.play(Transform(current_matrix_group, matrix_group4), FadeOut(r2_rect, r3_rect))
        self.wait(2)
        current_matrix_group = matrix_group4
        
        # Back Substitution Introduction
        back_sub_intro = Text("Giải bằng phương pháp thế ngược:", font_size=32, color=GREEN).to_edge(UP, buff=0.5)
        self.play(Transform(title, back_sub_intro))
        self.wait(1)

        # Equations from the final matrix
        eq_final_3_str = "-4z = -20"
        eq_final_2_str = "3y+5z=34"
        eq_final_1_str = "x+y+z=9"

        eq_final_3 = MathTex(eq_final_3_str, font_size=40, color=WHITE)
        eq_final_2 = MathTex(eq_final_2_str, font_size=40, color=WHITE)
        eq_final_1 = MathTex(eq_final_1_str, font_size=40, color=WHITE)

        eq_final_group = VGroup(eq_final_1, eq_final_2, eq_final_3).arrange(DOWN, buff=0.5)
        eq_final_group.next_to(current_matrix_group, RIGHT, buff=1.5)
        
        self.play(
            current_matrix_group.animate.to_edge(LEFT, buff=0.5), 
            FadeIn(eq_final_group[2], shift=RIGHT), 
            run_time=2
        )
        self.wait(1)

        # Solve for z
        z_eq_mobj = eq_final_group[2]
        z_step1 = MathTex("-4z = -20", font_size=40, color=WHITE)
        z_step2 = MathTex("z = \\frac{-20}{-4}", font_size=40, color=WHITE)
        z_solution_val = MathTex("z = 5", font_size=40, color=YELLOW)

        z_calc_objects = VGroup(z_step1, z_step2, z_solution_val).arrange(DOWN, buff=0.2)
        z_calc_objects.next_to(z_eq_mobj, RIGHT, buff=0.5)
        
        current_z_calc_mobject = z_calc_objects[0].copy().move_to(z_calc_objects[0])
        self.play(Write(current_z_calc_mobject))
        self.wait(1)
        self.play(Transform(current_z_calc_mobject, z_calc_objects[1].copy().move_to(z_calc_objects[1])))
        self.wait(1)
        self.play(Transform(current_z_calc_mobject, z_calc_objects[2].copy().move_to(z_calc_objects[2])))
        self.wait(1.5)
        final_z_solution_mobject = current_z_calc_mobject

        # Solve for y
        self.play(FadeIn(eq_final_group[1], shift=RIGHT))
        y_eq_mobj = eq_final_group[1]
        
        y_step1 = MathTex("3y+5z=34", font_size=40, color=WHITE)
        y_step2 = MathTex("3y+5(5)=34", font_size=40, color=WHITE)
        y_step3 = MathTex("3y+25=34", font_size=40, color=WHITE)
        y_step4 = MathTex("3y=34-25", font_size=40, color=WHITE)
        y_step5 = MathTex("3y=9", font_size=40, color=WHITE)
        y_solution_val = MathTex("y=3", font_size=40, color=YELLOW)
        
        y_calc_objects = VGroup(y_step1, y_step2, y_step3, y_step4, y_step5, y_solution_val).arrange(DOWN, buff=0.2)
        y_calc_objects.next_to(y_eq_mobj, RIGHT, buff=0.5)

        current_y_calc_mobject = y_calc_objects[0].copy().move_to(y_calc_objects[0])
        self.play(Write(current_y_calc_mobject))
        self.wait(1)
        
        for i in range(1, len(y_calc_objects)):
            self.play(Transform(current_y_calc_mobject, y_calc_objects[i].copy().move_to(y_calc_objects[i])))
            self.wait(1)
        final_y_solution_mobject = current_y_calc_mobject
        self.wait(0.5)

        # Solve for x
        self.play(FadeIn(eq_final_group[0], shift=RIGHT))
        x_eq_mobj = eq_final_group[0]

        x_step1 = MathTex("x+y+z=9", font_size=40, color=WHITE)
        x_step2 = MathTex("x+3+5=9", font_size=40, color=WHITE)
        x_step3 = MathTex("x+8=9", font_size=40, color=WHITE)
        x_step4 = MathTex("x=9-8", font_size=40, color=WHITE)
        x_solution_val = MathTex("x=1", font_size=40, color=YELLOW)

        x_calc_objects = VGroup(x_step1, x_step2, x_step3, x_step4, x_solution_val).arrange(DOWN, buff=0.2)
        x_calc_objects.next_to(x_eq_mobj, RIGHT, buff=0.5)

        current_x_calc_mobject = x_calc_objects[0].copy().move_to(x_calc_objects[0])
        self.play(Write(current_x_calc_mobject))
        self.wait(1)

        for i in range(1, len(x_calc_objects)):
            self.play(Transform(current_x_calc_mobject, x_calc_objects[i].copy().move_to(x_calc_objects[i])))
            self.wait(1)
        final_x_solution_mobject = current_x_calc_mobject
        self.wait(0.5)
        
        # Cleanup intermediate objects
        self.play(
            FadeOut(current_matrix_group), 
            FadeOut(eq_final_group), 
            FadeOut(final_z_solution_mobject), 
            FadeOut(final_y_solution_mobject), 
            FadeOut(final_x_solution_mobject)
        )
        
        # Final Answer
        final_answer_text = Text("Vậy nghiệm của hệ phương trình là:", font_size=36, color=GREEN)
        final_answer_values = MathTex("x=1, y=3, z=5", font_size=48, color=YELLOW)
        
        final_answer_group = VGroup(final_answer_text, final_answer_values).arrange(DOWN, buff=0.5)
        final_answer_group.move_to(ORIGIN)

        self.play(Transform(title, final_answer_text)) 
        self.play(Write(final_answer_values))
        self.wait(3)