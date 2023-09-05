import tkinter as tk
from pathlib import Path

from src import game_app


def main():
    root = tk.Tk()
    database_path = Path("./assets/database/test_typing.db")
    _ = game_app.TypingGameApp(root, database_path)
    root.mainloop()


if __name__ == "__main__":
    main()
