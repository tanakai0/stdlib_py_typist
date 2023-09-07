import tkinter as tk

from src import game_app


def main():
    root = tk.Tk()
    _ = game_app.TypingGameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
