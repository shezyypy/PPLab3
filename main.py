import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import traceback
import time
import sys

# Константы уровней
LEVELS = {
    "Easy": (9, 9, 10),
    "Medium": (16, 16, 40),
    "Hard": (16, 30, 99)
}

class Cell:
    def __init__(self):
        self.is_mine = False
        self.opened = False
        self.flagged = False
        self.adjacent = 0

class Minesweeper:
    CLOSED_COLOR = "#b0b0b0"  # тёмно-серый для закрытых клеток
    OPEN_COLOR = "#e0e0e0"  # светло-серый для открытых клеток
    FLAG_COLOR = "#ff2400"  # алый для флага

    def __init__(self, master):
        self.master = master
        self.master.title("Сапер")
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # статус и параметры игры
        self.rows, self.cols, self.mines = LEVELS["Easy"]
        self.buttons = {}
        self.cells = []
        self.started = False
        self.start_time = None
        self.timer_job = None

        self.create_menu()
        self.create_status_bar()
        self.create_board_frame()
        self.new_game(self.rows, self.cols, self.mines)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая — Easy", command=lambda: self.new_level("Easy"))
        game_menu.add_command(label="Новая — Medium", command=lambda: self.new_level("Medium"))
        game_menu.add_command(label="Новая — Hard", command=lambda: self.new_level("Hard"))
        game_menu.add_separator()
        game_menu.add_command(label="Пользовательская...", command=self.custom_game)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.master.quit)
        menubar.add_cascade(label="Игра", menu=game_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Сбросить окно...", command=self.reset_window_size)
        menubar.add_cascade(label="Настройки", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Правила", command=self.show_rules)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.master.config(menu=menubar)

    def create_status_bar(self):
        status_frame = tk.Frame(self.frame)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.mines_var = tk.StringVar(value=f"Мины: {self.mines}")
        self.time_var = tk.StringVar(value="Время: 0s")
        self.msg_var = tk.StringVar(value="")
        tk.Label(status_frame, textvariable=self.mines_var).pack(side=tk.LEFT, padx=5)
        tk.Label(status_frame, textvariable=self.time_var).pack(side=tk.LEFT, padx=5)
        tk.Label(status_frame, textvariable=self.msg_var).pack(side=tk.RIGHT, padx=5)

    def create_board_frame(self):
        # контейнер для сетки, который можно масштабировать
        self.board_container = tk.Frame(self.frame)
        self.board_container.pack(fill=tk.BOTH, expand=True)

    def new_level(self, level_name):
        try:
            r, c, m = LEVELS[level_name]
            self.new_game(r, c, m)
        except Exception as e:
            self._handle_exception(e)

    def custom_game(self):
        try:
            r = simpledialog.askinteger("Пользовательская", "Число строк (5-30):", parent=self.master, minvalue=5, maxvalue=30)
            if r is None:
                return
            c = simpledialog.askinteger("Пользовательская", "Число столбцов (5-50):", parent=self.master, minvalue=5, maxvalue=50)
            if c is None:
                return
            max_mines = max(1, r * c - 1)
            m = simpledialog.askinteger("Пользовательская", f"Число мин (1-{max_mines}):", parent=self.master, minvalue=1, maxvalue=max_mines)
            if m is None:
                return
            self.new_game(r, c, m)
        except Exception as e:
            self._handle_exception(e)

    def reset_window_size(self):
        try:
            self.master.geometry("")  # сбросить до дефолтного
            self.msg_var.set("Размер окна сброшен.")
        except Exception as e:
            self._handle_exception(e)

    def show_rules(self):
        rules = ("Правила Сапёра:\n\n"
                 "- Откройте все клетки, не содержащие мин.\n"
                 "- Левый клик: открыть клетку.\n"
                 "- Правый клик: поставить/снять флажок.\n"
                 "- Число на клетке = количество мин в соседних 8 клетках.\n")
        messagebox.showinfo("Правила", rules)

    def show_about(self):
        messagebox.showinfo("О программе", "Сапер (Tkinter) — учебная реализация.\nCreated for lab work.")

    def new_game(self, rows, cols, mines):
        try:
            self.rows = rows
            self.cols = cols
            self.mines = mines
            self.mines_var.set(f"Мины: {self.mines}")
            self.stop_timer()

            # очистка старых виджетов
            for widget in self.board_container.winfo_children():
                widget.destroy()
            self.buttons.clear()
            self.cells = [[Cell() for _ in range(cols)] for __ in range(rows)]

            # сетка кнопок
            for r in range(rows):
                self.board_container.grid_rowconfigure(r, weight=1)
                for c in range(cols):
                    self.board_container.grid_columnconfigure(c, weight=1)
                    btn = tk.Button(
                        self.board_container,
                        text="",
                        relief=tk.RAISED,
                        bg=self.CLOSED_COLOR,
                        activebackground=self.CLOSED_COLOR
                    )
                    btn.grid(row=r, column=c, sticky="nsew")
                    # биндим клики
                    btn.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_left_click(rr, cc))
                    btn.bind("<Button-3>", lambda e, rr=r, cc=c: self.on_right_click(rr, cc))
                    btn.bind("<Double-Button-1>", lambda e, rr=r, cc=c: self.on_double_click(rr, cc))
                    self.buttons[(r, c)] = btn

            # расстановка мин (отложим до первого клика, чтобы первая клетка не была миной)
            self.started = False
            self.msg_var.set("Новая игра. Сделайте ход.")
            self.update_timer_display(0)
        except Exception as e:
            self._handle_exception(e)

    def place_mines(self, first_r, first_c):
        # размещаем мин, исключая первую открытую клетку и её соседей, чтобы первый ход был безопасен
        try:
            positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
            # исключаем (first_r, first_c) и его соседей
            safe = set()
            for rr in range(first_r-1, first_r+2):
                for cc in range(first_c-1, first_c+2):
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        safe.add((rr, cc))
            available = [p for p in positions if p not in safe]
            if self.mines > len(available):
                # если число мин слишком велико, просто разрешим размещение везде (за исключением первой)
                available = [p for p in positions if p != (first_r, first_c)]
            mine_positions = random.sample(available, self.mines)
            for (r, c) in mine_positions:
                self.cells[r][c].is_mine = True
            # посчитать соседние числа
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.cells[r][c].is_mine:
                        continue
                    count = 0
                    for rr in range(r-1, r+2):
                        for cc in range(c-1, c+2):
                            if 0 <= rr < self.rows and 0 <= cc < self.cols:
                                if self.cells[rr][cc].is_mine:
                                    count += 1
                    self.cells[r][c].adjacent = count
        except Exception as e:
            self._handle_exception(e)

    def on_left_click(self, r, c):
        try:
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return
            cell = self.cells[r][c]
            if cell.flagged or cell.opened:
                return
            if not self.started:
                self.place_mines(r, c)
                self.started = True
                self.start_time = time.time()
                self.run_timer()

            if cell.is_mine:
                self.reveal_mine(r, c)
                self.game_over(False)
            else:
                self.open_cell(r, c)
                if self.check_win():
                    self.game_over(True)
        except Exception as e:
            self._handle_exception(e)

    def on_right_click(self, r, c):
        try:
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return
            cell = self.cells[r][c]
            if cell.opened:
                return
            cell.flagged = not cell.flagged
            self.update_button(r, c)
            remaining = self.count_remaining_mines()
            self.mines_var.set(f"Мины: {remaining}")
        except Exception as e:
            self._handle_exception(e)

    def on_double_click(self, r, c):
        try:
            # если ячейка открыта и число флагов вокруг равно её числу, открыть соседние
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return
            if not self.cells[r][c].opened:
                return
            needed = self.cells[r][c].adjacent
            flags = 0
            for rr in range(r-1, r+2):
                for cc in range(c-1, c+2):
                    if 0 <= rr < self.rows and 0 <= cc < self.cols:
                        if self.cells[rr][cc].flagged:
                            flags += 1
            if flags == needed:
                for rr in range(r-1, r+2):
                    for cc in range(c-1, c+2):
                        if 0 <= rr < self.rows and 0 <= cc < self.cols:
                            if not self.cells[rr][cc].flagged and not self.cells[rr][cc].opened:
                                self.on_left_click(rr, cc)
        except Exception as e:
            self._handle_exception(e)

    def open_cell(self, r, c):
        try:
            cell = self.cells[r][c]
            if cell.opened or cell.flagged:
                return
            cell.opened = True
            btn = self.buttons[(r, c)]
            btn.config(
                relief=tk.SUNKEN,
                state=tk.DISABLED,
                bg=self.OPEN_COLOR,
                activebackground=self.OPEN_COLOR
            )
            if cell.adjacent > 0:
                btn.config(text=str(cell.adjacent))
            else:
                btn.config(text="")
                # рекурсивно открыть соседние пустые
                for rr in range(r-1, r+2):
                    for cc in range(c-1, c+2):
                        if 0 <= rr < self.rows and 0 <= cc < self.cols:
                            if not self.cells[rr][cc].opened:
                                self.open_cell(rr, cc)
        except Exception as e:
            self._handle_exception(e)

    def reveal_mine(self, r, c):
        try:
            # показать все мины
            for rr in range(self.rows):
                for cc in range(self.cols):
                    if self.cells[rr][cc].is_mine:
                        btn = self.buttons[(rr, cc)]
                        btn.config(text="*", relief=tk.SUNKEN, disabledforeground="red")
            # показать взорванную как X
            btn = self.buttons[(r, c)]
            btn.config(text="X", disabledforeground="black")
        except Exception as e:
            self._handle_exception(e)

    def update_button(self, r, c):
        try:
            cell = self.cells[r][c]
            btn = self.buttons[(r, c)]
            if cell.opened:
                if cell.adjacent > 0:
                    btn.config(
                        text=str(cell.adjacent),
                        relief=tk.SUNKEN,
                        state=tk.DISABLED,
                        bg=self.OPEN_COLOR
                    )
                else:
                    btn.config(
                        text="",
                        relief=tk.SUNKEN,
                        state=tk.DISABLED,
                        bg=self.OPEN_COLOR
                    )
            else:
                if cell.flagged:
                    btn.config(
                        text="⚑",
                        bg=self.FLAG_COLOR,
                        activebackground=self.FLAG_COLOR
                    )
                else:
                    btn.config(
                        text="",
                        relief=tk.RAISED,
                        state=tk.NORMAL,
                        bg=self.CLOSED_COLOR,
                        activebackground=self.CLOSED_COLOR
                    )

        except Exception as e:
            self._handle_exception(e)

    def count_remaining_mines(self):
        # простая оценка: мин - флаги
        flags = sum(1 for r in range(self.rows) for c in range(self.cols) if self.cells[r][c].flagged)
        return max(0, self.mines - flags)

    def check_win(self):
        try:
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.cells[r][c]
                    if not cell.is_mine and not cell.opened:
                        return False
            return True
        except Exception as e:
            self._handle_exception(e)
            return False

    def game_over(self, win):
        try:
            self.stop_timer()
            if win:
                self.msg_var.set("Вы выиграли! Поздравляем.")
                messagebox.showinfo("Игра окончена", "Вы выиграли!")
            else:
                self.msg_var.set("Вы проиграли.")
                messagebox.showinfo("Игра окончена", "Вы проиграли.")
            # после окончания игры сделать кнопки неактивными
            for r in range(self.rows):
                for c in range(self.cols):
                    btn = self.buttons[(r, c)]
                    btn.config(state=tk.DISABLED)
        except Exception as e:
            self._handle_exception(e)

    def run_timer(self):
        try:
            def tick():
                try:
                    if not self.started:
                        return
                    elapsed = int(time.time() - self.start_time)
                    self.update_timer_display(elapsed)
                    self.timer_job = self.master.after(1000, tick)
                except Exception as e:
                    self._handle_exception(e)
            tick()
        except Exception as e:
            self._handle_exception(e)

    def stop_timer(self):
        try:
            if self.timer_job:
                self.master.after_cancel(self.timer_job)
                self.timer_job = None
            self.started = False
            self.start_time = None
        except Exception as e:
            self._handle_exception(e)

    def update_timer_display(self, seconds):
        try:
            self.time_var.set(f"Время: {seconds}s")
        except Exception as e:
            self._handle_exception(e)


    def _handle_exception(self, e):
        # Универсальная обработка ошибок: логируем и показываем пользователю, но не вылетаем.
        tb = traceback.format_exc()
        print("Exception:", str(e), file=sys.stderr)
        print(tb, file=sys.stderr)
        # показываем краткое сообщение пользователю (не раскрывая стек, если не нужно)
        try:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}\n(подробности в консоли)")
        except Exception:
            # если даже messagebox сломался, просто проигнорируем (чтобы не вызвать новый исключ)
            pass


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x450")
    app = Minesweeper(root)
    root.mainloop()
