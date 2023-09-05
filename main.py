import tkinter as tk
from pathlib import Path

from src import game


def main():
    root = tk.Tk()
    database_path = Path("./assets/database/typing_game.db")
    _ = game.TypingGameApp(root, database_path)
    root.mainloop()


if __name__ == "__main__":
    main()
