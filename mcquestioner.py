import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import random

class MCQuestioner:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Quiz App")
        
        # Full screen setup
        self.root.state('zoomed')
        
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Initialize variables
        self.questions = []
        self.current_question = 0
        self.user_answers = {}  # Changed to dictionary to store answers with question index
        self.score = 0
        self.incorrect_indices = []
        self.current_review_index = 0
        self.mode = 'quiz'  # Mode can be 'quiz', 'review', or 'finished'

        # Create layout
        self.score_label = tk.Label(self.frame, text=f"Score: {self.score}/0", font=("Arial", 16), anchor="e")
        self.score_label.pack(anchor="ne", padx=20, pady=10)
        
        self.question_label = tk.Label(self.frame, text="", font=("Arial", 20), anchor="center", justify="center", wraplength=800)
        self.question_label.pack(pady=20)

        self.options_var = tk.StringVar()
        self.option_buttons = [tk.Radiobutton(self.frame, variable=self.options_var, value=letter, font=("Arial", 16), anchor="w") for letter in ['a', 'b', 'c', 'd', 'e']]
        for btn in self.option_buttons:
            btn.pack(anchor="center", pady=5)

        self.feedback_label = tk.Label(self.frame, text="", font=("Arial", 18))
        self.feedback_label.pack(pady=20)

        self.explanation_label = tk.Label(self.frame, text="", font=("Arial", 16), wraplength=800, justify="center")
        self.explanation_label.pack(pady=20)

        self.submit_button = tk.Button(self.frame, text="Submit Answer", font=("Arial", 16), command=self.submit_answer)
        self.submit_button.pack(pady=20)

        self.prev_button = tk.Button(self.frame, text="Previous Question", font=("Arial", 16), command=self.prev_question, state="disabled")
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.next_button = tk.Button(self.frame, text="Next Question", font=("Arial", 16), command=self.next_question, state="disabled")
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.load_button = tk.Button(self.frame, text="Load CSV Files", font=("Arial", 16), command=self.load_csv)
        self.load_button.pack(pady=20)

        self.review_button = tk.Button(self.frame, text="Review Incorrect Answers", font=("Arial", 16), command=self.review_incorrect, state="disabled")
        self.review_button.pack(pady=20)

    def load_csv(self):
        #reset all variables
        self.current_question = 0
        self.user_answers = {}
        self.score = 0
        self.incorrect_indices = []
        self.current_review_index = 0
        self.questions = []
        self.mode = 'quiz'

        file_paths = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        for file_path in file_paths:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                question = {
                    'content': row['question_content'],
                    'choices': [row['choice_a'], row['choice_b'], row['choice_c'], row['choice_d'], row['choice_e']],
                    'correct_answer': row['correct_answer'],
                    'explanation': row.get('explanation', '')  # Optional explanation field
                }
                self.questions.append(question)
        random.shuffle(self.questions)
        self.load_button.config(state="disabled")
        
        # Update score label with total number of questions
        self.score_label.config(text=f"Score: {self.score}/{len(self.questions)}")
        self.show_question()

    def show_question(self):
        self.feedback_label.config(text="")
        self.explanation_label.config(text="")
        question = self.questions[self.current_question]
        self.question_label.config(text=f"Q{self.current_question + 1}: {question['content']}")
        for i, choice in enumerate(question['choices']):
            self.option_buttons[i].config(text=f"{chr(97 + i)}. {choice}")
            self.option_buttons[i].pack(anchor="center", pady=5)
        # Hide unused option buttons
        for i in range(len(question['choices']), len(self.option_buttons)):
            self.option_buttons[i].pack_forget()

        if self.mode in ['quiz', 'finished']:
            # Check if the current question has been answered
            if self.current_question in self.user_answers:
                # Show user's previous answer
                user_answer = self.user_answers[self.current_question]['user_answer']
                correct_answer = question['correct_answer']
                explanation = question.get('explanation', '')
                self.options_var.set(user_answer)
                if user_answer == correct_answer:
                    self.feedback_label.config(text="Correct!", fg="green")
                else:
                    self.feedback_label.config(text=f"Wrong! Correct answer is {correct_answer}", fg="red")
                self.explanation_label.config(text=f"Explanation: {explanation}")
                self.submit_button.config(state="disabled")
            else:
                # Question not answered yet
                self.options_var.set("")
                self.feedback_label.config(text="")
                self.explanation_label.config(text="")
                self.submit_button.config(state="normal")
        elif self.mode == 'review':
            # In review mode, always show the user's answer and feedback
            index_in_user_answers = self.current_question
            user_answer = self.user_answers[index_in_user_answers]['user_answer']
            correct_answer = question['correct_answer']
            explanation = question.get('explanation', '')
            self.options_var.set(user_answer)
            if user_answer == correct_answer:
                self.feedback_label.config(text="Correct!", fg="green")
            else:
                self.feedback_label.config(text=f"Wrong! Correct answer is {correct_answer}", fg="red")
            self.explanation_label.config(text=f"Explanation: {explanation}")
            self.submit_button.config(state="disabled")

        # Enable/disable navigation buttons
        if self.mode in ['quiz', 'finished']:
            self.prev_button.config(state="normal" if self.current_question > 0 else "disabled")
            self.next_button.config(state="normal" if self.current_question < len(self.questions) - 1 else "disabled")
        elif self.mode == 'review':
            self.prev_button.config(state="normal" if self.current_review_index > 0 else "disabled")
            self.next_button.config(state="normal" if self.current_review_index < len(self.incorrect_indices) - 1 else "disabled")

    def submit_answer(self):
        selected_answer = self.options_var.get()
        if not selected_answer:
            messagebox.showwarning("No Answer", "Please select an answer.")
            return

        # Check if the question has already been answered
        if self.current_question in self.user_answers:
            messagebox.showinfo("Already Answered", "You have already answered this question.")
            self.submit_button.config(state="disabled")
            return

        correct_answer = self.questions[self.current_question]['correct_answer']
        explanation = self.questions[self.current_question].get('explanation', '')

        # Store the user's answer and whether it was correct
        is_correct = selected_answer == correct_answer
        self.user_answers[self.current_question] = {
            'user_answer': selected_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': explanation
        }

        if is_correct:
            self.score += 1
            self.feedback_label.config(text="Correct!", fg="green")
        else:
            self.feedback_label.config(text=f"Wrong! Correct answer is {correct_answer}", fg="red")

        # Show explanation
        self.explanation_label.config(text=f"Explanation: {explanation}")

        # Update score tracker
        self.score_label.config(text=f"Score: {self.score}/{len(self.questions)}")

        # Disable submit button
        self.submit_button.config(state="disabled")
        # Enable navigation buttons
        self.prev_button.config(state="normal" if self.current_question > 0 else "disabled")
        self.next_button.config(state="normal" if self.current_question < len(self.questions) - 1 else "disabled")

        # Check if all questions have been answered
        if len(self.user_answers) == len(self.questions):
            self.finish_quiz()

    def prev_question(self):
        if self.mode in ['quiz', 'finished']:
            if self.current_question > 0:
                self.current_question -= 1
                self.show_question()
        elif self.mode == 'review':
            if self.current_review_index > 0:
                self.current_review_index -= 1
                self.current_question = self.incorrect_indices[self.current_review_index]
                self.show_question()

    def next_question(self):
        if self.mode in ['quiz', 'finished']:
            if self.current_question < len(self.questions) - 1:
                self.current_question += 1
                self.show_question()
        elif self.mode == 'review':
            if self.current_review_index < len(self.incorrect_indices) - 1:
                self.current_review_index += 1
                self.current_question = self.incorrect_indices[self.current_review_index]
                self.show_question()

    def finish_quiz(self):
        messagebox.showinfo("Quiz Finished", f"Your Score: {self.score}/{len(self.questions)}")
        self.review_button.config(state="normal")
        self.submit_button.config(state="disabled")
        self.load_button.config(state="normal")
        self.mode = 'finished'
        self.show_question()  # Refresh to ensure correct state of buttons

    def review_incorrect(self):
        # Collect indices of incorrect answers
        self.incorrect_indices = [index for index, answer in self.user_answers.items() if not answer['is_correct']]
        if not self.incorrect_indices:
            messagebox.showinfo("Review", "No incorrect answers to review.")
            return

        self.mode = 'review'
        self.current_review_index = 0
        self.current_question = self.incorrect_indices[self.current_review_index]
        self.load_button.config(state="normal")
        self.show_question()
        messagebox.showinfo("Review Mode", "You are now reviewing your incorrect answers.")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = MCQuestioner(root)
    root.mainloop()