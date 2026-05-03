from db_manager import DatabaseManager

db = DatabaseManager(password='password') 

width, height = 5, 5
test_grid = [[(True, 1.0) for _ in range(width)] for _ in range(height)]
test_grid[2][2] = (False, 1.0)

db.save_grid(test_grid, width, height)
print("Сохранено")

loaded = db.load_grid(width, height)
for y in range(height):
    row = ''
    for x in range(width):
        walkable, _ = loaded[y][x]
        row += '#' if not walkable else '.'
    print(row)

db.close()