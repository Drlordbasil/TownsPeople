from inventory import InventoryItem

class Environment:
    def __init__(self, grid_size):
        self.agents = []
        self.messages = []
        self.items = self.initialize_items()
        self.commands = self.initialize_commands()
        self.grid = self.initialize_grid(grid_size)
        self.grid_size = grid_size

    def initialize_items(self):
        return [
            InventoryItem("wood", 10),
            InventoryItem("stone", 5),
            InventoryItem("hammer", 2),
            InventoryItem("nails", 20),
            InventoryItem("paint", 3),
            InventoryItem("brush", 3),
            InventoryItem("laptop_with_ai", 1),
            InventoryItem("apples", 10),
            InventoryItem("bananas", 5),
            InventoryItem("oranges", 5),
            InventoryItem("pineapple", 2),
            InventoryItem("mangoes", 3),
            InventoryItem("grapes", 5),
            InventoryItem("strawberries", 5),
            InventoryItem("blueberries", 5),
            InventoryItem("raspberries", 5),
            InventoryItem("blackberries", 5),
            InventoryItem("peaches", 5),
            InventoryItem("plums", 5),
            InventoryItem("cherries", 5),
            InventoryItem("pears", 5),
            InventoryItem("watermelon", 5),
            InventoryItem("cantaloupe", 5),
            InventoryItem("honeydew", 5),
            InventoryItem("kiwi", 5),
            InventoryItem("papaya", 5),
            InventoryItem("guava", 5),
            InventoryItem("passion_fruit", 5),
            InventoryItem("dragon_fruit", 5),
            InventoryItem("star_fruit", 5),
            InventoryItem("lychee", 5),
            InventoryItem("mangosteen", 5),
            InventoryItem("durian", 5),
            InventoryItem("jackfruit", 5),
            InventoryItem("pomegranate", 5),
            InventoryItem("coconut", 5),
            InventoryItem("avocado", 5),
            InventoryItem("lemon", 5),
            InventoryItem("lime", 5),
            InventoryItem("grapefruit", 5),
            InventoryItem("tangerine", 5),
            InventoryItem("kumquat", 5),
            InventoryItem("apricot", 5),
        ]

    def initialize_commands(self):
        return [
            "take {item}",
            "put {item}",
            "inventory",
            "examine {item}",
            "use {item}",
            "give {quantity} {item} to {agent}",
            "ask {agent} for {quantity} {item}",
            "trade {quantity} {item} for {quantity} {item} with {agent}",
            "accept trade from {agent}",
            "help",
            "think",
        ]

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
            if agent.position is not None and self.get_distance(position, agent.position) <= radius:
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
            if agent.name != message.sender:
                agent.receive_message(message)

    def get_item(self, item_name):
        return next((item for item in self.items if item.name == item_name), None)

    def remove_item(self, item_name, quantity):
        item = self.get_item(item_name)
        if item and item.quantity >= quantity:
            item.quantity -= quantity
            if item.quantity == 0:
                self.items.remove(item)
            return True
        return False

    def add_item(self, item_name, quantity):
        item = self.get_item(item_name)
        if item:
            item.quantity += quantity
        else:
            self.items.append(InventoryItem(item_name, quantity))

    def list_items(self):
        return "Available items: " + ", ".join(f"{item.name} ({item.quantity})" for item in self.items)

    def list_commands(self):
        return "Available commands: " + ", ".join(self.commands)
