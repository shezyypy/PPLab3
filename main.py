import tkinter as tk
from tkinter import messagebox, simpledialog
import random


class Cell:
    def __init__(self):
        self.is_mine = False
        self.opened = False
        self.flagged = False
        self.adjacent = 0


class Minesweeper:
    def __init__(self, master):
        self.master = master
        self.master.title("Сапер")

        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.rows = 9
        self.cols = 9
        self.mines = 10

        self.create_menu()
        self.create_status_bar()
        self.create_board_frame()
        self.new_game()

    # --------------------- GUI -----------------------

    def create_menu(self):
        menubar = tk.Menu(self.master)

        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая", command=self.new_game)
        game_menu.add_command(label="Пользовательская...", command=self.custom_game)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.master.quit)
        menubar.add_cascade(label="Игра", menu=game_menu)

        self.master.config(menu=menubar)

    def create_status_bar(self):
        bar = tk.Frame(self.frame)
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.mines_var = tk.StringVar(value=f"Мины: {self.mines}")
        tk.Label(bar, textvariable=self.mines_var).pack(side=tk.LEFT, padx=5)

    def create_board_frame(self):
        self.board_container = tk.Frame(self.frame)
        self.board_container.pack(fill=tk.BOTH, expand=True)

    # ------------------- ИГРА ---------------------------

    def new_game(self):
        for w in self.board_container.winfo_children():
            w.destroy()

        self.cells = [[Cell() for _ in range(self.cols)] for __ in range(self.rows)]

        self.buttons = {}
        for r in range(self.rows):
            self.board_container.grid_rowconfigure(r, weight=1)
            for c in range(self.cols):
                self.board_container.grid_columnconfigure(c, weight=1)

                btn = tk.Button(self.board_container, text="", width=2, height=1)
                btn.grid(row=r, column=c, sticky="nsew")

                self.buttons[(r, c)] = btn

        self.mines_var.set(f"Мины: {self.mines}")

    def custom_game(self):
        r = simpledialog.askinteger("Строки", "Введите высоту (5–30):", minvalue=5, maxvalue=30)
        if r is None:
            return
        c = simpledialog.askinteger("Столбцы", "Введите ширину (5–50):", minvalue=5, maxvalue=50)
        if c is None:
            return
        m = simpledialog.askinteger("Мины", "Введите количество мин:", minvalue=1, maxvalue=r * c - 1)
        if m is None:
            return

        self.rows, self.cols, self.mines = r, c, m
        self.new_game()

    # ----------------------------------------------------

    def place_mines(self, first_r, first_c):
        """Размещаем мины, избегая первой нажатой клетки"""

        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        if (first_r, first_c) in positions:
            positions.remove((first_r, first_c))

        mines = random.sample(positions, self.mines)

        for r, c in mines:
            self.cells[r][c].is_mine = True

        # Подсчет соседних мин
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].is_mine:
                    continue

                count = 0
                for rr in range(r - 1, r + 2):
                    for cc in range(c - 1, c + 2):
                        if 0 <= rr < self.rows and 0 <= cc < self.cols:
                            if self.cells[rr][cc].is_mine:
                                count += 1

                self.cells[r][c].adjacent = count


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x450")
    app = Minesweeper(root)
    root.mainloop()
