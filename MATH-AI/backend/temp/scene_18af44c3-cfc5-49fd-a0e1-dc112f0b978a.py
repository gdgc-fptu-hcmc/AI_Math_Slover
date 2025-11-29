from manim import *

config.background_color = "#0f172a"

class MathAnimation(Scene):
    def construct(self):
        # Title
        title = Text("Giải Hệ Phương Trình Tuyến Tính", font_size=40, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Problem Equations
        eq1 = MathTex("x+y+z=9")
        eq2 = MathTex("2x+5y+7z=52")
        eq3 = MathTex("2x+y-z=0")
        
        equations = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.5)
        equations.next_to(title, DOWN, buff=1)
        self.play(Write(equations))
        self.wait(2)

        # Augmented Matrix Label
        matrix_label = Text("Ma trận bổ sung:", font_size=32).next_to(equations, DOWN, buff=1)
        self.play(FadeIn(matrix_label))
        self.wait(1)

        # Initial Augmented Matrix
        matrix_data_0 = [
            [1, 1, 1, 9],
            [2, 5, 7, 52],
            [2, 1, -1, 0]
        ]
        matrix_0 = Matrix(matrix_data_0, h_buff=1.0, v_buff=0.8)
        matrix_0.next_to(matrix_label, DOWN, buff=0.5)
        self.play(Create(matrix_0))
        self.wait(2)

        # --- Gaussian Elimination Steps ---

        # Step 1: R2 <- R2 - 2R1
        step1_op_label = Text("Bước 1: R2 \\leftarrow R2 - 2R1", font_size=32, color=BLUE)
        step1_op_label.next_to(matrix_0, DOWN, buff=1.0)
        self.play(Write(step1_op_label))
        self.wait(2)

        matrix_data_1 = [
            [1, 1, 1, 9],
            [0, 3, 5, 34], # R2 - 2R1: (2-2, 5-2, 7-2, 52-18) = (0, 3, 5, 34)
            [2, 1, -1, 0]
        ]
        matrix_1 = Matrix(matrix_data_1, h_buff=1.0, v_buff=0.8)
        matrix_1.move_to(matrix_0)
        self.play(Transform(matrix_0, matrix_1))
        self.wait(2)
        
        # Step 2: R3 <- R3 - 2R1
        step2_op_label = Text("Bước 2: R3 \\leftarrow R3 - 2R1", font_size=32, color=BLUE)
        step2_op_label.move_to(step1_op_label)
        self.play(Transform(step1_op_label, step2_op_label))
        self.wait(2)

        matrix_data_2 = [
            [1, 1, 1, 9],
            [0, 3, 5, 34],
            [0, -1, -3, -18] # R3 - 2R1: (2-2, 1-2, -1-2, 0-18) = (0, -1, -3, -18)
        ]
        matrix_2 = Matrix(matrix_data_2, h_buff=1.0, v_buff=0.8)
        matrix_2.move_to(matrix_0)
        self.play(Transform(matrix_0, matrix_2))
        self.wait(2)

        # Step 3: R3 <- 3R3 + R2
        step3_op_label = Text("Bước 3: R3 \\leftarrow 3R3 + R2", font_size=32, color=BLUE)
        step3_op_label.move_to(step1_op_label)
        self.play(Transform(step1_op_label, step3_op_label))
        self.wait(2)

        matrix_data_3 = [
            [1, 1, 1, 9],
            [0, 3, 5, 34],
            [0, 0, -4, -20] # 3R3+R2: (0+0, -3+3, -9+5, -54+34) = (0, 0, -4, -20)
        ]
        matrix_3 = Matrix(matrix_data_3, h_buff=1.0, v_buff=0.8)
        matrix_3.move_to(matrix_0)
        self.play(Transform(matrix_0, matrix_3))
        self.wait(2)
        
        # Step 4: R3 <- (-1/4)R3
        step4_op_label = Text("Bước 4: R3 \\leftarrow (-1/4)R3", font_size=32, color=BLUE)
        step4_op_label.move_to(step1_op_label)
        self.play(Transform(step1_op_label, step4_op_label))
        self.wait(2)

        matrix_data_4 = [
            [1, 1, 1, 9],
            [0, 3, 5, 34],
            [0, 0, 1, 5] # (-1/4)R3: (0, 0, 1, 5)
        ]
        matrix_4 = Matrix(matrix_data_4, h_buff=1.0, v_buff=0.8)
        matrix_4.move_to(matrix_0)
        self.play(Transform(matrix_0, matrix_4))
        self.wait(2)

        self.play(FadeOut(step1_op_label)) # Fade out the last step label

        # --- Back Substitution ---
        back_sub_label = Text("Thế ngược để tìm nghiệm:", font_size=36, color=YELLOW)
        back_sub_label.next_to(matrix_0, DOWN, buff=1.0)
        self.play(Write(back_sub_label))
        self.wait(2)

        # Solve for z
        z_equation_text = MathTex("0x + 0y + 1z = 5")
        z_solution_text = MathTex("\\Rightarrow z = 5")
        z_solution = VGroup(z_equation_text, z_solution_text).arrange(RIGHT, buff=0.2)
        z_solution.next_to(back_sub_label, DOWN, buff=0.5)
        self.play(Write(z_solution))
        self.wait(2)

        # Solve for y
        y_eq_step1 = MathTex("0x + 3y + 5z = 34").next_to(z_solution, DOWN, buff=0.7)
        y_eq_step2 = MathTex("3y + 5(5) = 34").move_to(y_eq_step1)
        y_eq_step3 = MathTex("3y + 25 = 34").move_to(y_eq_step1)
        y_eq_step4 = MathTex("3y = 9").move_to(y_eq_step1)
        y_eq_step5 = MathTex("y = 3").move_to(y_eq_step1)
        
        self.play(Write(y_eq_step1))
        self.wait(1)
        self.play(Transform(y_eq_step1, y_eq_step2))
        self.wait(1)
        self.play(Transform(y_eq_step1, y_eq_step3))
        self.wait(1)
        self.play(Transform(y_eq_step1, y_eq_step4))
        self.wait(1)
        self.play(Transform(y_eq_step1, y_eq_step5))
        self.wait(2)

        # Solve for x
        x_eq_step1 = MathTex("x + y + z = 9").next_to(y_eq_step1, DOWN, buff=0.7)
        x_eq_step2 = MathTex("x + 3 + 5 = 9").move_to(x_eq_step1)
        x_eq_step3 = MathTex("x + 8 = 9").move_to(x_eq_step1)
        x_eq_step4 = MathTex("x = 1").move_to(x_eq_step1)
        
        self.play(Write(x_eq_step1))
        self.wait(1)
        self.play(Transform(x_eq_step1, x_eq_step2))
        self.wait(1)
        self.play(Transform(x_eq_step1, x_eq_step3))
        self.wait(1)
        self.play(Transform(x_eq_step1, x_eq_step4))
        self.wait(2)
        
        # Clear the screen for final answer
        self.play(FadeOut(back_sub_label, z_solution, y_eq_step1, x_eq_step1, matrix_0, matrix_label, equations))
        
        # Final Answer
        final_answer_label = Text("Nghiệm của hệ phương trình:", font_size=36, color=GREEN).to_center().shift(UP*1.5)
        final_answer = MathTex("x = 1, \\quad y = 3, \\quad z = 5", font_size=48, color=YELLOW).next_to(final_answer_label, DOWN, buff=0.5)
        
        self.play(Write(final_answer_label))
        self.play(Write(final_answer))
        self.wait(3)