import tkinter as tk
from tkinter import messagebox

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Quiz")
        
        self.questions = {
            'easy': [
                ("What is 7 multiplied by 9?", "63", "7 multiplied by 9 equals 63."),
                ("Which of the following is an even number?", "24", "24 is an even number."),
                # Add more easy questions
            ],
            'medium': [
                ("If a rectangle has a length of 8 units and a width of 5 units, what is its perimeter?", "26", "Perimeter of the rectangle = 2 * (length + width) = 2 * (8 + 5) = 26."),
                ("What is the value of 3 squared?", "9", "3 squared equals 9."),
                
            ],
            'hard': [
                ("If a car travels at a speed of 60 miles per hour, how far will it travel in 2.5 hours?", "150", "Distance = speed × time = 60 × 2.5 = 150 miles."),
                ("What is the value of √(16^2 - 9^2)?", "15", "√(16^2 - 9^2) = √(256 - 81) = √175 ≈ 15."),
                
            ],
        }
        
        self.category_order = ['easy', 'medium', 'hard']
        self.current_category_index = 0
        self.current_question_index = 0
        self.correct_answers = 0
        
        self.label = tk.Label(root, text="Welcome to the Adaptive Quiz!")
        self.label.pack(pady=10)
        
        self.question_label = tk.Label(root, text="")
        self.question_label.pack(pady=5)
        
        self.answer_entry = tk.Entry(root)
        self.answer_entry.pack(pady=5)
        
        self.submit_button = tk.Button(root, text="Submit Answer", command=self.check_answer)
        self.submit_button.pack(pady=10)
        
        self.load_next_question()

    def load_next_question(self):
        if self.current_category_index < len(self.category_order):
            category = self.category_order[self.current_category_index]
            question_list = self.questions[category]
            question, _, _ = question_list[self.current_question_index]
            
            self.question_label.config(text=question)
        else:
            self.display_final_results()

    def check_answer(self):
        if self.current_category_index < len(self.category_order):
            category = self.category_order[self.current_category_index]
            question_list = self.questions[category]
            _, correct_answer, explanation = question_list[self.current_question_index]
            
            user_answer = self.answer_entry.get().strip()
            is_correct = user_answer == correct_answer
            self.show_result_message(is_correct, explanation)
            
            if is_correct:
                self.correct_answers += 1
                
                if self.current_category_index == 0 and self.current_question_index == 0:
                    self.current_category_index = 1
                    self.current_question_index = 0
                else:
                    self.current_question_index += 1
                    if self.current_question_index >= len(question_list):
                        self.current_question_index = 0
                        self.current_category_index += 1
                        if self.current_category_index == 1 and question_list == self.questions['medium']:
                            self.current_category_index = 2
            else:
                if self.current_category_index == 1:
                    self.current_category_index = 0
                    self.current_question_index = 0
                
            self.answer_entry.delete(0, tk.END)
            self.load_next_question()
        else:
            self.display_final_results()
            
    def show_result_message(self, is_correct, explanation):
        result_text = "Correct!" if is_correct else "Incorrect."
        result_text += "\n" + explanation
        messagebox.showinfo("Result", result_text)
            
    def display_final_results(self):
        result_message = f"You answered {self.correct_answers} questions correctly!\n"
        
        if self.correct_answers == len(self.questions['hard']):
            result_message += "Congratulations! You've mastered the quiz!"
        elif self.correct_answers >= len(self.questions['medium']):
            result_message += "Great job! You've shown strong knowledge!"
        elif self.correct_answers >= len(self.questions['easy']):
            result_message += "Well done! You're on the right track!"
        else:
            result_message += "Keep practicing and improving your skills!, you can always do better !"
        
        messagebox.showinfo("Quiz Results", result_message)
        self.root.destroy()

root = tk.Tk()
app = QuizApp(root)
root.mainloop()