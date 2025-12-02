import tkinter as tk
from tkinter import messagebox


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

        self.create_menu()
        self.create_status_bar()
        self.create_board_frame()
        self.new_game()

    def create_menu(self):
        menubar = tk.Menu(self.master)

        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая", command=self.new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.master.quit)
        menubar.add_cascade(label="Игра", menu=game_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=lambda: messagebox.showinfo("О программе", "Сапер"))
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.master.config(menu=menubar)

    def create_status_bar(self):
        status = tk.Frame(self.frame)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        self.msg_var = tk.StringVar(value="Готово")
        tk.Label(status, textvariable=self.msg_var).pack(side=tk.LEFT)

    def create_board_frame(self):
        self.board_container = tk.Frame(self.frame)
        self.board_container.pack(fill=tk.BOTH, expand=True)

    def new_game(self):
        # очистка старого поля
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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x450")
    app = Minesweeper(root)
    root.mainloop()
