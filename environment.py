class Environment:
    def __init__(self, grid_size):
        self.agents = []
        self.messages = []
        self.items = [
            {"name": "wood", "quantity": 10},
            {"name": "stone", "quantity": 5},
            {"name": "hammer", "quantity": 2},
            {"name": "nails", "quantity": 20},
            {"name": "paint", "quantity": 3},
            {"name": "brush", "quantity": 3},
            {"name": "Laptop With AI", "quantity": 1},
            {"name": "Apples", "quantity": 10},
            {"name": "Bananas", "quantity": 5},
            {"name": "Oranges", "quantity": 5},
            {"name": "Pineapple", "quantity": 2},
            {"name": "Mangoes", "quantity": 3},
            {"name": "Grapes", "quantity": 5},
            {"name": "Strawberries", "quantity": 5},
            {"name": "Blueberries", "quantity": 5},
            {"name": "Raspberries", "quantity": 5},
            {"name": "Blackberries", "quantity": 5},
            {"name": "Peaches", "quantity": 5},
            {"name": "Plums", "quantity": 5},
            {"name": "Cherries", "quantity": 5},
            {"name": "Pears", "quantity": 5},
            {"name": "Watermelon", "quantity": 5},
            {"name": "Cantaloupe", "quantity": 5},
            {"name": "Honeydew", "quantity": 5},
            {"name": "Kiwi", "quantity": 5},
            {"name": "Papaya", "quantity": 5},
            {"name": "Guava", "quantity": 5},
            {"name": "Passion Fruit", "quantity": 5},
            {"name": "Dragon Fruit", "quantity": 5},
            {"name": "Star Fruit", "quantity": 5},
            {"name": "Lychee", "quantity": 5},
            {"name": "Mangosteen", "quantity": 5},
            {"name": "Durian", "quantity": 5},
            {"name": "Jackfruit", "quantity": 5},
            {"name": "Pomegranate", "quantity": 5},
            {"name": "Coconut", "quantity": 5},
            {"name": "Avocado", "quantity": 5},
            {"name": "Lemon", "quantity": 5},
            {"name": "Lime", "quantity": 5},
            {"name": "Grapefruit", "quantity": 5},
            {"name": "Tangerine", "quantity": 5},
            {"name": "Kumquat", "quantity": 5},
            {"name": "Apricot", "quantity": 5},
        ]
        self.commands = [
            "take {item}",
            "put {item}",
            "inventory",
            "examine {item}",
            "use {item}",
            "give {item} to {agent}",
            "ask {agent} for {item}",
            "trade {item} with {agent}",
            "help",
            "think",
        ]
        self.grid = self.initialize_grid(grid_size)
        self.grid_size = grid_size

    def initialize_grid(self, grid_size):
        return [[None] * grid_size[1] for _ in range(grid_size[0])]

    def update_agent_position(self, agent, new_position):
        old_position = agent.position
        if old_position is not None:
            self.grid[old_position[0]][old_position[1]] = None
        self.grid[new_position[0]][new_position[1]] = agent
        agent.position = new_position

    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] is None

    def get_nearby_agents(self, position, radius=1):
        nearby_agents = []
        for agent in self.agents:
            if self.get_distance(position, agent.position) <= radius:
                nearby_agents.append(agent)
        return nearby_agents

    def get_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def add_agent(self, agent):
        self.agents.append(agent)
        print(f"Agent {agent.name} has been added to the environment.")

    def broadcast_message(self, message):
        self.messages.append(message)
        for agent in self.agents:
            if agent.name != message.split(":")[0]:
                agent.receive_message(message)

    def get_item(self, item_name):
        return next((item for item in self.items if item["name"] == item_name), None)

    def remove_item(self, item_name, quantity):
        item = self.get_item(item_name)
        if item and item["quantity"] >= quantity:
            item["quantity"] -= quantity
            if item["quantity"] == 0:
                self.items.remove(item)
            return True
        return False

    def add_item(self, item_name, quantity):
        item = self.get_item(item_name)
        if item:
            item["quantity"] += quantity
        else:
            self.items.append({"name": item_name, "quantity": quantity})

    def list_items(self):
        return "Available items: " + ", ".join(f"{item['name']} ({item['quantity']})" for item in self.items)

    def list_commands(self):
        return "Available commands: " + ", ".join(self.commands)