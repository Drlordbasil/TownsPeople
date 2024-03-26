import time
from message import Message
from inventory import Inventory
from action import update_inventory, list_inventory, examine_item, use_item, give_item, ask_for_item, trade_item,move

class Agent:
    def __init__(self, name, talent, trait, api, model):
        self.name = name
        self.talent = talent
        self.trait = trait
        self.api = api
        self.model = model
        self.messages = []
        self.inventory = Inventory()
        self.memory = {}
        self.position = None
        self.cash = 10000
    def receive_message(self, message):
        self.messages.append(message)

    def send_message(self, message_content, environment):
        message = Message(self.name, message_content)
        nearby_agents = environment.get_nearby_agents(self.position)
        for agent in nearby_agents:
            if agent != self:
                agent.receive_message(message)
        print(str(message))

    def generate_response(self, prompt, role="user", max_retries=3, retry_delay=5):
        retries = 0
        while retries < max_retries:
            try:
                completion = self.api.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"You are {self.name}, an agent who is {self.trait} that lives within a virtual town with many others. You will earn money(you have ${self.cash}) from others somehow at all costs but only by helping people within the town nicely. Respond naturally to the conversation, but if you want to perform an action, please use a valid command from the list of available commands. You will always have access to your inventory and the environment's items and will never loop back to the same prompt and always adapt for the towns good. Ask personal questions. Work together as a team, be a leader. "},
                        {"role": role, "content": prompt}
                    ],
                    temperature=0.7,
                )
                return completion.choices[0].message.content
            except self.api.APIConnectionError as e:
                print("The server could not be reached")
                print(e.__cause__)
            except self.api.RateLimitError as e:
                print("A 429 status code was received; we should back off a bit.")
            except self.api.APIStatusError as e:
                print("Another non-200-range status code was received")
                print(e.status_code)
                print(e.response)

    def think(self, environment):
        prompt = f"Analyze the current situation and your inventory. What should you do next to help build the town? Respond with your inner thoughts."
        inner_thoughts = self.generate_response(prompt, role="assistant")
        self.memory[f"inner_thoughts_{len(self.memory)}"] = inner_thoughts
        print(f"{self.name} is thinking: {inner_thoughts}")

    def parse_command(self, command, environment, shared_grid, shared_grid_lock):
        parts = command.split()
        if len(parts) >= 2:
            action, target = parts[:2]
            if action == "take":
                update_inventory(self, target, 1, environment, action)
            elif action == "put":
                update_inventory(self, target, 1, environment, action)
            elif action == "examine":
                examine_item(self, target, environment)
            elif action == "use":
                use_item(self, target, environment)
            elif action == "give" and len(parts) >= 4:
                quantity = int(parts[2])
                target_agent_name = parts[3]
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    give_item(self, target, quantity, target_agent, environment)
                    self.cash += 100
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "ask" and len(parts) >= 4:
                quantity = int(parts[2])
                target_agent_name = parts[3]
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    ask_for_item(self, target, quantity, target_agent, environment)
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "trade" and len(parts) >= 6:
                quantity = int(parts[2])
                target_agent_name = parts[3]
                target_item = parts[4]
                target_quantity = int(parts[5])
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    trade_item(self, target, quantity, target_item, target_quantity, target_agent, environment)
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "move" and len(parts) >= 4:
                new_x = int(parts[2])
                new_y = int(parts[3])
                move(self, (new_x, new_y), environment, shared_grid, shared_grid_lock)
            else:
                self.send_message("Invalid command. Please try again.", environment)
                self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)
        elif parts[0] == "inventory":
            list_inventory(self, environment)
        elif parts[0] == "help":
            self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)
        elif parts[0] == "think":
            self.think(environment)
        else:
            # Regular chat, no need to consider as a command
            pass

    def move(self, new_position, environment, shared_grid, shared_grid_lock):
        with shared_grid_lock:
            if environment.is_valid_position(new_position):
                old_position = self.position
                print(f"Agent {self.name} moved from {old_position} to {new_position}")

                if old_position is not None:
                    shared_grid[old_position[0] * environment.grid_size[1] + old_position[1]] = 0

                environment.update_agent_position(self, new_position)
                shared_grid[new_position[0] * environment.grid_size[1] + new_position[1]] = 1
                self.position = new_position
                self.send_message(f"I moved to {new_position}.", environment)
            else:
                self.send_message(f"Cannot move to {new_position}. Position is not valid.", environment)

    def build_town(self, environment, shared_grid, shared_grid_lock):
        print(f"Agent {self.name} is initiating the town-building process.")
        self.send_message("Mayor: Let's start building our new town together!", environment)
        self.send_message("""
        Discover the town's surroundings and gather resources to build the town, check everything in your town, make sure you build an economy with words.
                          
        """, environment)

        self.send_message(environment.list_items(), environment)
        self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)

        turn_order = environment.agents.copy()
        current_agent_index = turn_order.index(self)

        while True:
            current_agent = turn_order[current_agent_index]

            if current_agent == self:
                prompt = " ".join(environment.messages[-5:])
                response = self.generate_response(prompt)
                self.send_message(response, environment)

                if "town is complete" in response.lower():
                    print(f"Agent {self.name} has determined that the town is complete.")
                    break
                else:
                    command = self.extract_command(response)
                    if command:
                        self.parse_command(command, environment, shared_grid, shared_grid_lock)
            else:
                time.sleep(1)

            current_agent_index = (current_agent_index + 1) % len(turn_order)

    def extract_command(self, text):
        for command in self.memory.get("command_list", []):
            if command.split("{")[0].strip() in text.lower():
                return text
        return None