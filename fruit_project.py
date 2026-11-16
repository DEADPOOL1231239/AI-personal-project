
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

from PIL import Image, ImageTk
from fruit_classification import predict_fruit

from groq import Groq
from dotenv import load_dotenv


load_dotenv()
client = Groq()

APP_TITLE = "FruitAI | Apple & Orange Classifier"
PREVIEW_SIZE = (320, 240)

# COLORS
BG = "#F3F4F8"
WHITE = "#FFFFFF"
NAVY = "#20243A"
PURPLE = "#7057D9"
LIGHT_PURPLE = "#F0ECFF"
TEXT = "#252942"
GRAY = "#85899B"
GREEN = "#159B72"


class FruitApp:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1050x780")
        self.root.minsize(850, 680)
        self.root.configure(bg=BG)

        self.preview_image = None
        self.history = []

        # HEADER
        header = tk.Frame(root, bg=NAVY, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🍎 FruitAI",
            font=("Segoe UI", 23, "bold"),
            fg=WHITE,
            bg=NAVY
        ).pack(side="left", padx=30, pady=20)

        tk.Label(
            header,
            text="SMART FRUIT CLASSIFICATION",
            font=("Segoe UI", 10, "bold"),
            fg="#B9B4E9",
            bg=NAVY
        ).pack(side="right", padx=30)

        # MAIN AREA
        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=22, pady=20)

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # LEFT CLASSIFICATION CARD
        left = tk.Frame(
            main,
            bg=WHITE,
            highlightbackground="#E4E5ED",
            highlightthickness=1
        )
        left.grid(
            row=0, column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        tk.Label(
            left,
            text="Fruit Classification",
            font=("Segoe UI", 19, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", padx=22, pady=(25, 5))

        tk.Label(
            left,
            text="Upload an image to identify your fruit.",
            font=("Segoe UI", 10),
            fg=GRAY,
            bg=WHITE
        ).pack(anchor="w", padx=22, pady=(0, 18))

        # IMAGE PREVIEW
        self.image_label = tk.Label(
            left,
            text="🍎   🍊\n\nUpload an apple or orange image",
            font=("Segoe UI", 12),
            fg=GRAY,
            bg="#F7F7FC",
            width=40,
            height=12,
            relief="flat",
            highlightbackground="#DCD9EF",
            highlightthickness=2
        )
        self.image_label.pack(padx=20, pady=5, fill="x")

        # UPLOAD BUTTON
        self.choose_button = tk.Button(
            left,
            text="＋  Choose Fruit Image",
            command=self.choose_image,
            font=("Segoe UI", 11, "bold"),
            bg=PURPLE,
            fg=WHITE,
            activebackground="#5942BC",
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=12
        )
        self.choose_button.pack(fill="x", padx=20, pady=15)

        # RESULT CARD
        result_card = tk.Frame(
            left,
            bg=LIGHT_PURPLE,
            padx=15,
            pady=15
        )
        result_card.pack(fill="x", padx=20, pady=8)

        tk.Label(
            result_card,
            text="CLASSIFICATION RESULT",
            font=("Segoe UI", 9, "bold"),
            fg=PURPLE,
            bg=LIGHT_PURPLE
        ).pack(anchor="w")

        self.result_label = tk.Label(
            result_card,
            text="Waiting for image...",
            font=("Segoe UI", 17, "bold"),
            fg=TEXT,
            bg=LIGHT_PURPLE
        )
        self.result_label.pack(anchor="w", pady=7)

        self.confidence_label = tk.Label(
            result_card,
            text="Confidence: -",
            font=("Segoe UI", 11),
            fg=TEXT,
            bg=LIGHT_PURPLE
        )
        self.confidence_label.pack(anchor="w")

        self.path_label = tk.Label(
            left,
            text="No image selected",
            font=("Segoe UI", 8),
            fg=GRAY,
            bg=WHITE,
            wraplength=350
        )
        self.path_label.pack(pady=10)

        # RIGHT CHATBOT CARD
        right = tk.Frame(
            main,
            bg=WHITE,
            highlightbackground="#E4E5ED",
            highlightthickness=1
        )
        right.grid(
            row=0, column=1,
            sticky="nsew",
            padx=(10, 0)
        )

        tk.Label(
            right,
            text="AI Assistant  ✨",
            font=("Segoe UI", 19, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", padx=20, pady=(25, 4))

        tk.Label(
            right,
            text="Ask anything about Apple & Orange AI.",
            font=("Segoe UI", 10),
            fg=GRAY,
            bg=WHITE
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # CHAT FRAME
        chat_frame = tk.Frame(right, bg="#F7F7FC")
        chat_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side="right", fill="y")

        self.chat_box = tk.Text(
            chat_frame,
            wrap="word",
            font=("Segoe UI", 10),
            bg="#F7F7FC",
            fg=TEXT,
            relief="flat",
            padx=12,
            pady=12,
            state="disabled",
            yscrollcommand=scrollbar.set
        )
        self.chat_box.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(command=self.chat_box.yview)

        self.chat_box.tag_config(
            "user",
            foreground=PURPLE,
            font=("Segoe UI", 10, "bold")
        )

        self.chat_box.tag_config(
            "bot",
            foreground=GREEN,
            font=("Segoe UI", 10, "bold")
        )

        self.add_message(
            "AI Assistant",
            "Hello! 👋 I'm your FruitAI assistant. Ask me anything about apples, oranges, binary classification or machine learning."
        )

        # INPUT AREA
        input_frame = tk.Frame(right, bg=WHITE)
        input_frame.pack(fill="x", padx=15, pady=18)

        self.chat_input = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1,
            bg="#F7F7FC",
            fg=TEXT
        )
        self.chat_input.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=12,
            padx=(0, 8)
        )

        self.chat_input.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        self.send_button = tk.Button(
            input_frame,
            text="Send ➤",
            command=self.send_message,
            font=("Segoe UI", 10, "bold"),
            bg=PURPLE,
            fg=WHITE,
            activebackground="#5942BC",
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=10
        )
        self.send_button.pack(side="right")

        tk.Label(
            right,
            text="Powered by Groq AI",
            font=("Segoe UI", 9),
            fg=GRAY,
            bg=WHITE
        ).pack(pady=(0, 12))

    # IMAGE CLASSIFICATION

    def choose_image(self):
        image_path = filedialog.askopenfilename(
            title="Choose Fruit Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"),
                ("All files", "*.*"),
            ],
        )

        if not image_path:
            return

        self.show_preview(image_path)
        self.predict(image_path)

    def show_preview(self, image_path):
        image = Image.open(image_path).convert("RGB")
        image.thumbnail(PREVIEW_SIZE)

        self.preview_image = ImageTk.PhotoImage(image)

        self.image_label.configure(
            image=self.preview_image,
            text="",
            width=320,
            height=240
        )

        self.path_label.configure(
            text=str(Path(image_path))
        )

    def predict(self, image_path):
        try:
            result = predict_fruit(image_path)

        except Exception as error:
            messagebox.showerror(
                "Prediction Error",
                str(error)
            )
            return

        self.result_label.configure(
            text=f"🍎  Fruit: {result['fruit_class']}"
        )

        self.confidence_label.configure(
            text=f"Confidence: {result['confidence']:.2%}"
        )

    # GROQ CHATBOT

    def send_message(self):
        user_input = self.chat_input.get().strip()

        if not user_input:
            return

        self.chat_input.delete(0, tk.END)

        self.add_message("You", user_input)

        self.history.append({
            "role": "user",
            "content": user_input
        })

        self.send_button.configure(state="disabled")

        threading.Thread(
            target=self.chat_response,
            daemon=True
        ).start()

    def chat_response(self):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=self.history
            )

            reply = response.choices[0].message.content

            self.history.append({
                "role": "assistant",
                "content": reply
            })

            self.root.after(
                0,
                lambda: self.show_reply(reply)
            )

        except Exception as error:
            self.root.after(
                0,
                lambda: self.show_error(str(error))
            )

    def add_message(self, sender, message):
        self.chat_box.configure(state="normal")

        tag = "user" if sender == "You" else "bot"

        self.chat_box.insert(
            tk.END,
            sender + "\n",
            tag
        )

        self.chat_box.insert(
            tk.END,
            message + "\n\n"
        )

        self.chat_box.configure(state="disabled")
        self.chat_box.see(tk.END)

    def show_reply(self, reply):
        self.add_message("AI Assistant", reply)
        self.send_button.configure(state="normal")

    def show_error(self, error):
        self.add_message("Error", error)

        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()

        self.send_button.configure(state="normal")


def main():
    root = tk.Tk()
    app = FruitApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
