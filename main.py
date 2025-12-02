import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time


class Cell:
    def __init__(self):
        self.is_mine = False
        self.opened = False
               ...
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

        self.started = False
        self.start_time = None

        self.create_menu()
        self.create_status_bar()
        self.create_board_frame()
        self.new_game()

    # ------------------GUI

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
        self.time_var = tk.StringVar(value="Время: 0s")

        tk.Label(bar, textvariable=self.mines_var).pack(side=tk.LEFT, padx=5)
        tk.Label(bar, textvariable=self.time_var).pack(side=tk.LEFT, padx=5)

    def create_board_frame(self):
        self.board_container = tk.Frame(self.frame)
        self.board_container.pack(fill=tk.BOTH, expand=True)

    # -----------------ИГРА

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

                btn.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_left(rr, cc))
                btn.bind("<Button-3>", lambda e, rr=r, cc=c: self.on_right(rr, cc))

                self.buttons[(r, c)] = btn

        self.started = False
        self.start_time = None

        self.mines_var.set(f"Мины: {self.mines}")
        self.time_var.set("Время: 0s")

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

    # ----------------Минирование

    def place_mines(self, first_r, first_c):
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        positions.remove((first_r, first_c))

        mines = random.sample(positions, self.mines)

        for r, c in mines:
            self.cells[r][c].is_mine = True

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

    # -----------------Клики

    def on_left(self, r, c):
        cell = self.cells[r][c]

        if cell.flagged or cell.opened:
            return

        if not self.started:
            self.place_mines(r, c)
            self.started = True
            self.start_time = time.time()
            self.update_timer()

        if cell.is_mine:
            self.reveal_mines()
            messagebox.showinfo("Поражение", "Вы подорвались!")
            self.disable_all()
            return

        self.open_cell(r, c)

        if self.check_win():
            self.reveal_mines()
            messagebox.showinfo("Победа", "Вы выиграли!")
            self.disable_all()

    def on_right(self, r, c):
        cell = self.cells[r][c]
        if cell.opened:
            return

        cell.flagged = not cell.flagged
        self.buttons[(r, c)].config(text="⚑" if cell.flagged else "")

        self.mines_var.set(f"Мины: {self.mines - self.count_flags()}")

    # ----------------Открытие

    def open_cell(self, r, c):
        cell = self.cells[r][c]
        if cell.opened or cell.flagged:
            return

        cell.opened = True
        btn = self.buttons[(r, c)]
        btn.config(relief=tk.SUNKEN, state=tk.DISABLED)

        if cell.adjacent > 0:
            btn.config(text=str(cell.adjacent))
            return

        # Раскрытие пустых зон
        for rr in range(r - 1, r + 2):
            for cc in range(c - 1, c + 2):
                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                    if not self.cells[rr][cc].opened:
                        self.open_cell(rr, cc)

    # ----------------Служебные

    def reveal_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].is_mine:
                    self.buttons[(r, c)].config(text="*")

    def disable_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.buttons[(r, c)].config(state=tk.DISABLED)

    def count_flags(self):
        return sum(self.cells[r][c].flagged for r in range(self.rows) for c in range(self.cols))

    def check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r][c]
                if not cell.is_mine and not cell.opened:
                    return False
        return True

    def update_timer(self):
        if not self.started:
            return

        elapsed = int(time.time() - self.start_time)
        self.time_var.set(f"Время: {elapsed}s")

        self.master.after(1000, self.update_timer)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x450")
    app = Minesweeper(root)
    root.mainloop()
