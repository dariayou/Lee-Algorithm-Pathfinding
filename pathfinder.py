import heapq

def find_path(grid, start, goal):
    height = len(grid)
    width = len(grid[0])
    
    moves = [
        (1,0,1.0), (-1,0,1.0), (0,1,1.0), (0,-1,1.0),
        (1,1,1.41421356), (1,-1,1.41421356), (-1,1,1.41421356), (-1,-1,1.41421356),
        (2,1,2.23606798), (2,-1,2.23606798), (-2,1,2.23606798), (-2,-1,2.23606798),
        (1,2,2.23606798), (1,-2,2.23606798), (-1,2,2.23606798), (-1,-2,2.23606798)
    ]
    
    def is_step_possible(x, y, dx, dy):
        if abs(dx) + abs(dy) == 2:
            nx1, ny1 = x + dx, y
            nx2, ny2 = x, y + dy
            if not (0 <= nx1 < width and 0 <= ny1 < height and grid[ny1][nx1][0]):
                return False
            if not (0 <= nx2 < width and 0 <= ny2 < height and grid[ny2][nx2][0]):
                return False
        elif (abs(dx), abs(dy)) in [(2,1), (1,2)]:
            sign_x = 1 if dx > 0 else -1
            sign_y = 1 if dy > 0 else -1
            if abs(dx) == 2:
                mid1 = (x + sign_x, y)
                mid2 = (x + sign_x, y + sign_y)
            else:
                mid1 = (x, y + sign_y)
                mid2 = (x + sign_x, y + sign_y)
            for mx, my in [mid1, mid2]:
                if not (0 <= mx < width and 0 <= my < height and grid[my][mx][0]):
                    return False
        return True

    start_x, start_y = start
    goal_x, goal_y = goal
    
    def heuristic(x, y):
        return ((x - goal_x)**2 + (y - goal_y)**2)**0.5
    
    INF = float('inf')
    g_score = [[INF]*width for _ in range(height)]
    g_score[start_y][start_x] = 0
    f_score = [[INF]*width for _ in range(height)]
    f_score[start_y][start_x] = heuristic(start_x, start_y)
    
    parent = [[None]*width for _ in range(height)]
    open_set = [(f_score[start_y][start_x], start_x, start_y)]
    closed_set = set()
    
    while open_set:
        _, x, y = heapq.heappop(open_set)
        if (x, y) == goal:
            path = []
            while (x, y) != start:
                path.append((x, y))
                x, y = parent[y][x]
            path.append(start)
            path.reverse()
            return path
        if (x, y) in closed_set:
            continue
        closed_set.add((x, y))
        
        for dx, dy, step_cost in moves:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if not grid[ny][nx][0]:
                continue
            if not is_step_possible(x, y, dx, dy):
                continue
            cell_cost = grid[ny][nx][1]
            tentative_g = g_score[y][x] + step_cost * cell_cost
            if tentative_g < g_score[ny][nx]:
                parent[ny][nx] = (x, y)
                g_score[ny][nx] = tentative_g
                f = tentative_g + heuristic(nx, ny)
                f_score[ny][nx] = f
                heapq.heappush(open_set, (f, nx, ny))
    return None