from db_manager import DatabaseManager
from pathfinder import find_path

db = DatabaseManager(password='password')  

width, height = 5, 5
grid_data = db.load_grid(width, height)

start = (0, 0)
goal = (4, 4)
path = find_path(grid_data, start, goal)

if path:
    print("Путь найден:", path)
    display = [['.' for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if not grid_data[y][x][0]:
                display[y][x] = '#'
    for (x, y) in path:
        if display[y][x] == '.':
            display[y][x] = '*'
    for row in display:
        print(' '.join(row))
else:
    print("Путь не найден")

db.close()