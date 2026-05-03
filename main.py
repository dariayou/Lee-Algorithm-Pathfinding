import tkinter as tk
from tkinter import messagebox
from db_manager import DatabaseManager
from pathfinder import find_path

class LeeApp:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        
        self.width = 20    
        self.height = 15   
        self.cell_size = 35  
        self.grid = [[(True, 1.0) for _ in range(self.width)] for _ in range(self.height)]
        
        self.start = None
        self.goal = None
        self.path = None
        
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='white',
                                width=self.width*self.cell_size,
                                height=self.height*self.cell_size)
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<Button-3>", self.right_click)

        panel = tk.Frame(root)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Button(panel, text="Загрузить сетку", command=self.load_grid).pack(pady=5)
        tk.Button(panel, text="Сохранить сетку", command=self.save_grid).pack(pady=5)
        tk.Button(panel, text="Очистить путь", command=self.clear_path).pack(pady=5)
        tk.Button(panel, text="Найти путь", command=self.find_and_draw).pack(pady=5)
        tk.Button(panel, text="Сброс (стены удалить)", command=self.reset_walls).pack(pady=5)
        tk.Button(panel, text="Очистить старт/цель", command=self.reset_start_goal).pack(pady=5)
        
        self.status = tk.Label(panel, text="Левый клик: старт/цель | Правый: стена", fg="blue")
        self.status.pack(pady=10)
        
        self.draw_grid()
    
    def draw_grid(self):
        self.canvas.delete("all")
        for y in range(self.height):
            for x in range(self.width):
                walkable, cost = self.grid[y][x]
                if self.start == (x, y):
                    color = "green"
                elif self.goal == (x, y):
                    color = "red"
                elif self.path and (x, y) in self.path:
                    color = "blue"
                else:
                    if not walkable:
                        color = "gray"
                    else:
                        if cost == 3.0:
                            color = "light green"
                        elif cost == 0.5:
                            color = "light yellow"
                        else:
                            color = "white"
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        for i in range(self.width+1):
            self.canvas.create_line(i*self.cell_size, 0, i*self.cell_size, self.height*self.cell_size)
        for i in range(self.height+1):
            self.canvas.create_line(0, i*self.cell_size, self.width*self.cell_size, i*self.cell_size)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def left_click(self, event):
        x = int(self.canvas.canvasx(event.x) // self.cell_size)
        y = int(self.canvas.canvasy(event.y) // self.cell_size)
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.start is None:
                self.start = (x, y)
            elif self.goal is None:
                self.goal = (x, y)
            else:
                self.start = (x, y)
            self.path = None
            self.draw_grid()
    
    def right_click(self, event):
        x = int(self.canvas.canvasx(event.x) // self.cell_size)
        y = int(self.canvas.canvasy(event.y) // self.cell_size)
        if 0 <= x < self.width and 0 <= y < self.height:
            if (x, y) == self.start or (x, y) == self.goal:
                return
            walkable, cost = self.grid[y][x]
            self.grid[y][x] = (not walkable, cost)
            self.path = None
            self.draw_grid()
    
    def load_grid(self):
        try:
            loaded = self.db.load_grid(self.width, self.height)
            self.grid = loaded
            self.start = None
            self.goal = None
            self.path = None
            self.draw_grid()
            self.status.config(text="Сетка загружена из БД", fg="green")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))
    
    def save_grid(self):
        try:
            self.db.save_grid(self.grid, self.width, self.height)
            self.status.config(text="Сетка сохранена в БД", fg="green")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))
    
    def clear_path(self):
        self.path = None
        self.draw_grid()
    
    def reset_walls(self):
        for y in range(self.height):
            for x in range(self.width):
                walkable, cost = self.grid[y][x]
                self.grid[y][x] = (True, cost)
        self.path = None
        self.draw_grid()
    
    def reset_start_goal(self):
        self.start = None
        self.goal = None
        self.path = None
        self.draw_grid()
    
    def find_and_draw(self):
        if self.start is None or self.goal is None:
            messagebox.showwarning("Ошибка", "Выберите начальную и целевую точки")
            return
        if self.start == self.goal:
            messagebox.showinfo("Путь", "Начальная и целевая точки совпадают")
            self.path = []
            self.draw_grid()
            return
        if not self.grid[self.start[1]][self.start[0]][0]:
            messagebox.showerror("Ошибка", "Начальная точка - стена")
            return
        if not self.grid[self.goal[1]][self.goal[0]][0]:
            messagebox.showerror("Ошибка", "Целевая точка - стена")
            return
        
        path = find_path(self.grid, self.start, self.goal)
        if path is None:
            messagebox.showerror("Путь не найден", "Невозможно достичь цели")
            self.path = None
        else:
            self.path = path
            length = 0.0
            for i in range(len(path)-1):
                x1,y1 = path[i]
                x2,y2 = path[i+1]
                dx = abs(x2-x1)
                dy = abs(y2-y1)
                if dx+dy == 1:
                    step_len = 1.0
                elif dx==1 and dy==1:
                    step_len = 1.41421356
                else:
                    step_len = 2.23606798
                length += step_len
            self.status.config(text=f"Путь найден, длина {length:.3f}", fg="blue")
        self.draw_grid()

if __name__ == "__main__":
    db = DatabaseManager(password='password') 
    root = tk.Tk()
    root.title("Волновой алгоритм Ли")
    app = LeeApp(root, db)
    root.mainloop()
    db.close()