import random
import copy

THINK_AHEAD_STEPS = 5

class MCTSAgent(object):
    def __init__(self, runs):
        self.runs = runs

    def select_move(self, game_state):
        root = MCTSNode(Environment(game_state))
        for i in range(0, self.runs):
            node = root.select_node()
            env = node.simulate_random_game()
            node.record(env)
        return root.select_winning_move()

class MCTSNode(object):
    def __init__(self, environment, parent=None, move=None):
        self.environment = environment
        self.parent = parent
        self.move = move
        self.num_rollout = 0
        self.score = 0
        self.children = []
        self.unvisited_moves = ["up", "right", "down", "left"]

    def select_winning_move(self):
        print(f"MOVE: {list(map(lambda node: node.get_average_score(), self.children))}")
        print(f"MOVE: {list(map(lambda node: node.move, self.children))}")
        candidates = []
        max = -999
        for node in self.children:
            if node.get_average_score() > max:
                candidates = [node]
                max = node.get_average_score()
            elif node.get_average_score() == max:
                candidates.append(node)
        return random.choice(candidates).move

    def get_average_score(self):
        return self.score / self.num_rollout

    def select_node(self):
        if len(self.unvisited_moves) > 0:
            move = self.unvisited_moves.pop()
            new_environment = copy.deepcopy(self.environment)
            new_environment.apply_move(move)
            new_node = MCTSNode(new_environment, self, move)
            self.children.append(new_node)
            return new_node
        return random.choice(self.children)

    def record(self, env):
        node = self
        while node is not None:
            node.score += env.get_score()
            node.num_rollout += 1
            node = node.parent
    
    def simulate_random_game(self):
        env = copy.deepcopy(self.environment)
        if env.is_dead():
            return env
        for i in range(0, THINK_AHEAD_STEPS):
            move = random.choice(env.get_valid_moves(env.game_state["you"]["id"]))
            env.apply_move(move)
            if env.is_dead():
                break
        return env

class Environment(object):
    def __init__(self, game_state):
        self.game_state = game_state
        self.food_occupied = {}
        self.calculate_occupied()

    def get_score(self):
        if self.is_dead():
            return -9999
        return self.game_state["you"]["health"] + self.game_state["you"]["length"] * 10

    def apply_move(self, my_move):
        new_game_state = copy.deepcopy(self.game_state)
        new_game_state["board"]["snakes"] = []
        for snake in self.game_state["board"]["snakes"]:
            move = my_move if snake["id"] == self.game_state["you"]["id"] else random.choice(self.get_valid_moves(snake["id"]))
            new_snake = self.move_snake(snake, move)
            new_game_state["board"]["snakes"].append(new_snake)
            if snake["id"] == self.game_state["you"]["id"]:
                new_game_state["you"] = new_snake
        new_food = []
        for food in new_game_state["board"]["food"]:
            if not self.food_occupied["{0}+{1}".format(food["x"],food["y"])]:
                new_food.append(food)
        new_game_state["board"]["food"] = new_food
        self.remove_dead_snakes(new_game_state)
        # TODO: Generate new food
        self.game_state = new_game_state
        self.calculate_occupied()

    def remove_dead_snakes(self, new_game_state):
        snakes = copy.deepcopy(new_game_state["board"]["snakes"])
        new_game_state["board"]["snakes"] = []
        for snake in snakes:
            if not self.is_dead_snake(snake, snakes, new_game_state):
                new_game_state["board"]["snakes"].append(snake)
            elif (new_game_state["you"] is not None and snake["id"] == new_game_state["you"]["id"]):
                new_game_state["you"] = None

    def is_dead_snake(self, snake, snakes, game_state):
        head = snake["head"]
        head_in_bound = head["x"] >= 0 and head["x"] < game_state["board"]["width"] and head["y"] >= 0 and head["y"] < game_state["board"]["height"]
        has_health = snake["health"] > 0
        not_collided = True
        not_self_collided = True
        self_occupied = {}
        for other in snakes:
            if other["id"] == snake["id"]:
                continue
            for part in other["body"]:
                if head["x"] == part["x"] and head["y"] == part["y"]:
                    if part["x"] == other["head"]["x"] and part["y"] == other["head"]["y"]:
                        not_collided = snake["length"] > other["length"]
                    else:
                        not_collided = False
        for part in snake["body"]:
            key = "{0}+{1}".format(part["x"],part["y"])
            if key in self_occupied:
                not_self_collided = False
                break
            else:
                self_occupied[key] = True
        return not(head_in_bound and has_health and not_collided and not_self_collided)


    def move_snake(self, snake, move):
        new_snake = copy.deepcopy(snake)
        new_body = copy.deepcopy(snake["body"])
        if move == "up":
            new_snake["head"]["y"] += 1
        if move == "right":
            new_snake["head"]["x"] += 1
        if move == "down":
            new_snake["head"]["y"] -= 1
        if move == "left":
            new_snake["head"]["x"] -= 1
        new_head = new_snake["head"]
        if self.hit_food(new_head):
            new_snake["health"] = 100
            new_snake["length"] += 1
        else:
            new_snake["health"] -= 1
            new_body.pop()
        new_body.insert(0, new_snake["head"])
        new_snake["body"] = new_body
        return new_snake

    def hit_food(self, head):
        if ("{0}+{1}".format(head["x"],head["y"])) in self.food_occupied:
            self.food_occupied["{0}+{1}".format(head["x"],head["y"])] = True
            return True
        return False

    def get_valid_moves(self, snake_id):
        target_snake = None
        for snake in self.game_state["board"]["snakes"]:
            if snake["id"] == snake_id:
                target_snake = snake
        if target_snake == None:
            raise Exception("no target snake!")
        result = []
        head = target_snake["head"]
        if self.is_valid_move(head["x"], head["y"] + 1):
            result.append("up")
        if self.is_valid_move(head["x"] + 1, head["y"]):
            result.append("right")
        if self.is_valid_move(head["x"], head["y"] - 1):
            result.append("down")
        if self.is_valid_move(head["x"] - 1, head["y"]):
            result.append("left")
        # appends up if no valid moves
        if len(result) == 0:
            result.append("up")
        return result
    
    def is_valid_move(self, x, y):
        return x >= 0 and x < self.game_state["board"]["width"] and y >= 0 and y < self.game_state["board"]["height"] and (not ("{0}+{1}".format(x,y) in self.snake_occupied))
    
    def calculate_occupied(self):
        self.food_occupied = {}
        self.snake_occupied = {}
        for snake in self.game_state["board"]["snakes"]:
            for part in snake["body"]:
                self.snake_occupied["{0}+{1}".format(part["x"],part["y"])] = True
        for food in self.game_state["board"]["food"]:
            self.food_occupied["{0}+{1}".format(food["x"],food["y"])] = False

    def is_dead(self):
        return self.game_state["you"] is None
    
    def is_winner(self):
        return len(self.game_state["board"]["snakes"]) == 1 and self.game_state["board"]["snakes"][0]["id"] == self.game_state["you"]["id"]