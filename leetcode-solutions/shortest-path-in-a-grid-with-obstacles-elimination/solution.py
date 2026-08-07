class Solution:
    def shortestPath(self, grid: List[List[int]], k: int) -> int:
        if not grid or not grid[0]:
            return -1

        m, n = len(grid), len(grid[0])
        
        target = (m - 1, n - 1)

        queue = collections.deque()
        initial_state = (0, 0, k)
        queue.append(initial_state)

        distance = {}
        distance[initial_state] = 0
                
        DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while queue:
            x, y, k = queue.popleft()
            
            if (x, y) == target:
                return distance[(x, y, k)]
            
            for dx, dy in DIRECTIONS:
                adj_x = x + dx
                adj_y = y + dy

                if not (0 <= adj_x < len(grid) and 0 <= adj_y < len(grid[0])):
                    continue

                new_state = (adj_x, adj_y, k - grid[adj_x][adj_y])

                if new_state in distance:
                    continue
                
                if new_state[2] >= 0:
                    queue.append(new_state)
                    distance[new_state] = distance[(x, y, k)] + 1
        
        return -1
