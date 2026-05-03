import psycopg2

class DatabaseManager:
    def __init__(self, dbname='lee_algorithm', user='postgres', password='password', host='localhost'):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self.cur = self.conn.cursor()

    def load_grid(self, width, height):
        self.cur.execute("""
            SELECT g.x, g.y, g.walkable, s.cost_factor
            FROM grid g
            JOIN surface_types s ON g.surface_type_id = s.id
        """)
        rows = self.cur.fetchall()

        grid = [[(True, 1.0) for _ in range(width)] for _ in range(height)]
        for x, y, walkable, cost in rows:
            if 0 <= x < width and 0 <= y < height:
                grid[y][x] = (walkable, cost)
        return grid

    def save_grid(self, grid_data, width, height):
        self.cur.execute('DELETE FROM grid')
        for y in range(height):
            for x in range(width):
                walkable, cost = grid_data[y][x]
                surface_id = 1
                if cost == 3.0:
                    surface_id = 2
                elif cost == 0.5:
                    surface_id = 3
                self.cur.execute(
                    "INSERT INTO grid (x, y, walkable, surface_type_id) VALUES (%s, %s, %s, %s)",
                    (x, y, walkable, surface_id)
                )
        self.conn.commit()

    def update_cell(self, x, y, walkable, surface_type_id):
        self.cur.execute("""
            INSERT INTO grid (x, y, walkable, surface_type_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (x, y) DO UPDATE
            SET walkable = EXCLUDED.walkable, surface_type_id = EXCLUDED.surface_type_id
        """, (x, y, walkable, surface_type_id))
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()