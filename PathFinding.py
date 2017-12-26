class Node:

    def __init__(self, x, y, neighbors=[]):
        self.x = x
        self.y = y
        self.val = 9
        self.neighbors = neighbors


def make_graph(game_map):
    width = game_map.width
    height = game_map.height

    n = height
    m = width
    graph = [[Node(m, n) for j in range(m)] for i in range(n)]

    for i in range(n):
        for j in range(m):
            if (i >= 1):
                graph[n][m].neighbors.append(graph[n-1][m])
                graph[n-1][m].neighbors.append(graph[n][m])
            if (j >= 1):
                graph[n][m].neighbors.append(graph[n][m-1])
                graph[n][m-1].neighbors.append(graph[n][m])

    return graph

def make_mapping(game_map, graph, me):

    # 1 = friendly ship, 2 = enemy ship, 3 = planet
    for ship in self_all_ships():
        x = ship.x
        y = ship.y
        radius = ship.radius
        owner = ship.owner

        # round x and y to nearest integer
        j = round(x)
        i = round(y)
        graph[i][j].val = 1 if owner == me else 2

    for planet in self.all_planets():
        x = planet.x
        y = planet.y
        radius = planet.radius

        j = round(x)
        i = round(y)

        graph[i][j].val = 3

