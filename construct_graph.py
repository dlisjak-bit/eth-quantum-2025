from helper import placeholder_instructions
import itertools


class Spatial_node:
    def __init__(self, x, y, node_type):
        self.x = x
        self.y = y
        self.node_type = node_type
        if node_type == "standard":
            self.idle = False
        self.occupied: list[Ion] = []

    def store_neighbours(self, neighbours):
        self.neighbours = neighbours

    @staticmethod
    def find_neighbours(spatial_grid):
        for y in range(len(spatial_grid)):
            for x in range(len(spatial_grid[y])):
                current_node = spatial_grid[y][x]
                neighbours = []

                if current_node.node_type == "standard":
                    idle_node = Spatial_node(x, y, "idle")
                    current_node.idle = True
                    idle_node.store_neighbours([current_node])

                    neighbours.append(idle_node)

                possible_neigbours = [(-1, 0), (0, -1), (0, 1), (1, 0)]
                for i, j in possible_neigbours:
                    x_neigh = x + i
                    y_neigh = y + j
                    if x_neigh < 0 or y_neigh < 0:
                        continue
                    if (
                        len(spatial_grid) <= y_neigh
                        or len(spatial_grid[y_neigh]) <= x_neigh
                    ):
                        continue
                    neighbours.append(spatial_grid[y_neigh][x_neigh])

                current_node.store_neighbours(neighbours)

    @staticmethod
    def clear_occupied():
        for j in range(len(spatial_grid)):
            for i in range(len(spatial_grid[j])):
                spatial_grid[j][i].occupied = []

    @staticmethod
    def make_occupied(ions, spatial_grid):
        Spatial_node.clear_occupied()
        for ion in ions:
            spatial_grid[ion.y][ion.x].occupied.append(ion)


def create_spatial_grid(X=7, Y=5):
    spatial_grid = [[None for _ in range(X)] for _ in range(Y)]

    interactive = [(1, 1), (3, 1), (5, 1), (1, 3), (3, 3), (5, 3)]

    for j in range(len(spatial_grid)):
        for i in range(len(spatial_grid[j])):
            if (i, j) in interactive:
                node_type = "interactive"
            else:
                node_type = "standard"

            spatial_grid[j][i] = Spatial_node(i, j, node_type)

    Spatial_node.find_neighbours(spatial_grid)

    return spatial_grid


class Move:
    def __init__(self, ion, new_x, new_y, cost_change, execute):
        self.ion = ion
        self.new_x = new_x
        self.new_y = new_y
        self.cost_change = cost_change
        self.execute = execute

    def __str__(self):
        return ",".join([str(x) for x in [self.ion.ion_index, self.new_x, self.new_y, self.cost_change, self.execute]])


class Ion:
    def __init__(self, ion_index, x, y):
        self.ion_index = ion_index
        self.execution_index = 0
        self.cost = 0
        self.x = x
        self.y = y

    def make_move(self, move: Move, spatial_grid):
        og_node = spatial_grid[self.y][self.x]
        self.x = move.new_x
        self.y = move.new_y
        new_node = spatial_grid[self.y][self.x]
        if og_node.node_type == "idle":
            new_node.idle = False
        self.cost += move.cost_change
        if move.execute:
            self.execution_index += 1

    def find_moves(self, spatial_grid, instructions, ions):
        # REMINDER double MS1, MS2
        moves = []
        instruction = instructions[self.ion_index][self.execution_index]
        instruction_type = instruction[0]

        current_node = spatial_grid[self.y][self.x]

        if (
            current_node.node_type == "interaction"
            or current_node.node_type == "standard"
        ):
            cost_change = 0.02
        elif current_node.node_type == "idle":
            cost_change = 0.01

        execute = None
        if (instruction_type == "MS2" and current_node.occupied == 2 and current_node.node_type == "interaction"):
            execute = instruction_type
        if (instruction_type[:2] != "MS" and current_node.node_type == "standard"):
            execute = instruction_type

        move = Move(self, current_node.x, current_node.y, cost_change, execute=execute)
        moves.append(move)

        if instruction_type == "MS2":
            return moves

        for neighbour in current_node.neighbours:
            move_to = spatial_grid[neighbour.y][neighbour.x]
            if move_to.node_type == "standard" and move_to.idle:
                continue
            if len(move_to.occupied) == 0:
                execute = None
                if (instruction_type[:2] != "MS" and current_node.node_type == "standard"):
                    execute = instruction_type
                move = Move(
                    self, neighbour.x, neighbour.y, cost_change=0.03, execute=execute
                )
                moves.append(move)
            # Check for instruction time
            elif len(move_to.occupied) == 1 and move_to.node_type == "interaction" and instruction_type == "MS1":
                entangled = ions[instruction[1]]
                entangled_instruct = instructions[entangled.ion_index][
                    entangled.execution_index
                ]
                if (
                    entangled_instruct[0] != "MS1"
                    or entangled_instruct[1] != self.ion_index
                ): continue

                move = Move(
                    self, neighbour.x, neighbour.y, cost_change=0.03, execute="MS1"
                )
                moves.append(move)
            else: continue

        return moves


def filter_invalid(all_possible, instructions, ions, spatial_grid):
    actual = []
    n = 0
    for possible in all_possible:
        n += 1
        counter = dict()
        # Count positions in power
        for move in possible:
            hsh = str(move.new_x) + "|" + str(move.new_y)
            if hsh not in counter:
                counter[hsh] = [0, move]
            counter[hsh][0] += 1
        # find maximum value 
        max_value = max(counter.values(), key=lambda x: x[0])
        if max_value[0] < 2:
            actual.append(possible)
            continue
        if 2 < max_value[0]:
            raise ValueError("Shouldn't happen")
        two_together = filter(lambda x: x[0] == 2, counter.values())
        for n, move in two_together:
            if n == 2 and move.execute is not None and move.execute[:2] == "MS": continue

        actual.append(possible)

    return actual, n


N = 2
coords = [(2, 3), (1, 2), (5, 4), (4, 3), ()]

spatial_grid = create_spatial_grid()
ions = [Ion(i, coords[i][0], coords[i][1]) for i in range(N)]
Spatial_node.make_occupied(ions, spatial_grid)

moves = []
instructions = placeholder_instructions(N)
print(instructions[0][:5])
print(instructions[1][:5])

for ion in ions:
    moves.append(ion.find_moves(spatial_grid, instructions, ions))


all_possible = itertools.product(*moves)
filtered, n = filter_invalid(all_possible, instructions, ions, spatial_grid)
print(len(filtered), n)
for x in filtered:
    print(*x)


