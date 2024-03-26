import time
import random
from openai import OpenAI
from groq import Groq

class Environment:
    def __init__(self):
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


class Mayor:
    def __init__(self, name, api, model):
        self.name = name
        self.api = api
        self.model = model
        self.memory = {
            "command_list": [
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
            ],
            "help_instructions": [
                "To help the agents build their town, you can provide guidance and assistance.",
                "Encourage them to use the available commands to gather resources and construct buildings.",
                "If an agent is stuck or unsure what to do, offer suggestions and explain the commands.",
                "Monitor their progress and provide feedback and support when needed.",
                "Remember to be patient and understanding, as the agents are learning and working together.",
                "reember to keep them on task and focused on the goal of building the town."
            ],
        }

    def send_message(self, message, environment):
        environment.broadcast_message(f"{self.name}: {message}")
        print(f"{self.name}: {message}")

    def generate_response(self, prompt, role="user"):
        completion = self.api.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are {self.name}, the all-knowing guide and mayor. Provide helpful information and assistance to the agents building the town. Use your knowledge of command_list and help_instructions to guide them.{self.memory['help_instructions'],{self.memory['command_list']}}."},
                {"role": role, "content": prompt}
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content

    def provide_guidance(self, environment):
        prompt = " ".join(environment.messages[-5:])
        if any(command in prompt.lower() for command in self.memory["command_list"]):
            response = self.generate_response(prompt, role="assistant")
            self.send_message(response, environment)
            if "invalid command" in response.lower() or "help" in prompt.lower():
                self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)
                self.send_message("Remember to use the available commands to build the town effectively.", environment)


class Agent:
    def __init__(self, name, talent, trait, api, model):
        self.name = name
        self.talent = talent
        self.trait = trait
        self.api = api
        self.model = model
        self.messages = []
        self.inventory = []
        self.memory = {}

    def receive_message(self, message):
        self.messages.append(message)

    def send_message(self, message, environment):
        environment.broadcast_message(f"{self.name}: {message}")
        print(f"{self.name}: {message}")

    def generate_response(self, prompt, role="user", max_retries=3, retry_delay=5):
        retries = 0
        while retries < max_retries:
            try:
                completion = self.api.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"You are {self.name}, an agent who is {self.trait}. Respond naturally to the conversation, but if you want to perform an action, please use a valid command from the list of available commands. You will always have access to your inventory and the environment's items and will never loop back to the same prompt and always adapt for the towns good. Ask personal questions. Work together as a team, be a leader. "},
                        {"role": role, "content": prompt}
                    ],
                    temperature=0.7,
                )
                return completion.choices[0].message.content
            except self.api.APIConnectionError as e:
                print("The server could not be reached")
                print(e.__cause__)  # an underlying Exception, likely raised within httpx.
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

    def update_inventory(self, item_name, quantity, environment, action):
        if action == "take":
            if environment.remove_item(item_name, quantity):
                self.inventory.append({"name": item_name, "quantity": quantity})
                self.send_message(f"I took {quantity} {item_name} from the environment.", environment)
                self.memory[f"took_{item_name}_{quantity}"] = True
                print(f"Agent {self.name} took {quantity} {item_name} from the environment.")
            else:
                self.send_message(f"Not enough {item_name} available in the environment.", environment)
        elif action == "put":
            item = next((item for item in self.inventory if item["name"] == item_name), None)
            if item:
                if item["quantity"] >= quantity:
                    item["quantity"] -= quantity
                    if item["quantity"] == 0:
                        self.inventory.remove(item)
                    environment.add_item(item_name, quantity)
                    self.send_message(f"I put {quantity} {item_name} back in the environment.", environment)
                    self.memory[f"put_{item_name}_{quantity}"] = True
                    print(f"Agent {self.name} put {quantity} {item_name} back in the environment.")
                else:
                    self.send_message(f"I don't have enough {item_name} in my inventory.", environment)
            else:
                self.send_message(f"I don't have any {item_name} in my inventory.", environment)

    def list_inventory(self, environment):
        if self.inventory:
            inventory_list = ", ".join(f"{item['name']} ({item['quantity']})" for item in self.inventory)
            self.send_message(f"My inventory: {inventory_list}", environment)
            self.memory["inventory"] = self.inventory
            print(f"Agent {self.name} listed their inventory: {inventory_list}")
        else:
            self.send_message("My inventory is empty.", environment)
            self.memory["inventory"] = []

    def examine_item(self, item_name, environment):
        item = environment.get_item(item_name)
        if item:
            self.send_message(f"Examining {item_name}: It is a {item_name}. Quantity: {item['quantity']}.", environment)
            self.memory[f"examined_{item_name}"] = item
            print(f"Agent {self.name} examined {item_name}: {item}")
        else:
            self.send_message(f"There is no {item_name} in the environment.", environment)

    def use_item(self, item_name, environment):
        self.send_message(f"I'm using {item_name} to build the town.", environment)
        self.memory[f"used_{item_name}"] = True
        print(f"Agent {self.name} is using {item_name} to build the town.")

    def give_item(self, item_name, quantity, target_agent, environment):
        item = next((item for item in self.inventory if item["name"] == item_name), None)
        if item:
            if item["quantity"] >= quantity:
                item["quantity"] -= quantity
                if item["quantity"] == 0:
                    self.inventory.remove(item)
                target_agent.inventory.append({"name": item_name, "quantity": quantity})
                self.send_message(f"I gave {quantity} {item_name} to {target_agent.name}.", environment)
                target_agent.send_message(f"I received {quantity} {item_name} from {self.name}.", environment)
                self.memory[f"gave_{item_name}_{quantity}_to_{target_agent.name}"] = True
                target_agent.memory[f"received_{item_name}_{quantity}_from_{self.name}"] = True
                print(f"Agent {self.name} gave {quantity} {item_name} to {target_agent.name}.")
            else:
                self.send_message(f"I don't have enough {item_name} to give.", environment)
        else:
            self.send_message(f"I don't have any {item_name} to give.", environment)

    def ask_for_item(self, item_name, quantity, target_agent, environment):
        self.send_message(f"{target_agent.name}, can I have {quantity} {item_name} please?", environment)
        self.memory[f"asked_{target_agent.name}_for_{item_name}_{quantity}"] = True
        print(f"Agent {self.name} asked {target_agent.name} for {quantity} {item_name}.")

    def trade_item(self, item_name, quantity, target_item, target_quantity, target_agent, environment):
        self.send_message(f"{target_agent.name}, would you like to trade {quantity} {item_name} for {target_quantity} {target_item}?", environment)
        self.memory[f"proposed_trade_{quantity}_{item_name}_for_{target_quantity}_{target_item}_with_{target_agent.name}"] = True
        print(f"Agent {self.name} proposed a trade with {target_agent.name}.")
    def parse_command(self, command, environment):
        parts = command.split()
        if len(parts) >= 2:
            action, target = parts[:2]
            if action == "take":
                self.update_inventory(target, 1, environment, action)
            elif action == "put":
                self.update_inventory(target, 1, environment, action)
            elif action == "examine":
                self.examine_item(target, environment)
            elif action == "use":
                self.use_item(target, environment)
            elif action == "give" and len(parts) >= 4:
                quantity = int(parts[2])
                target_agent_name = parts[3]
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    self.give_item(target, quantity, target_agent, environment)
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "ask" and len(parts) >= 4:
                quantity = int(parts[2])
                target_agent_name = parts[3]
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    self.ask_for_item(target, quantity, target_agent, environment)
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "trade" and len(parts) >= 6:
                quantity = int(parts[2])
                target_agent_name = parts[3]
                target_item = parts[4]
                target_quantity = int(parts[5])
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    self.trade_item(target, quantity, target_item, target_quantity, target_agent, environment)
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            else:
                self.send_message("Invalid command. Please try again.", environment)
                self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)
        elif parts[0] == "inventory":
            self.list_inventory(environment)
        elif parts[0] == "help":
            self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)
        elif parts[0] == "think":
            self.think(environment)
        else:
            # Regular chat, no need to consider as a command
            pass

    def build_town(self, environment):
        print(f"Agent {self.name} is initiating the town-building process.")
        self.send_message("Mayor: Let's start building our new town together!", environment)
        self.send_message("""
                          
                          This process will extract your responses and commands to build the town. Below is the function that will be used to extract the commands from your responses.
                          Please review and understand how to do your commands based on the below function that is listening to your response:
                          '''python function
                                def parse_command(self, command, environment):
                                    parts = command.split()
                                    if len(parts) >= 2:
                                        action, target = parts[:2]
                                        if action == "take":
                                            self.update_inventory(target, 1, environment, action)
                                        elif action == "put":
                                            self.update_inventory(target, 1, environment, action)
                                        elif action == "examine":
                                            self.examine_item(target, environment)
                                        elif action == "use":
                                            self.use_item(target, environment)
                                        elif action == "give" and len(parts) >= 4:
                                            quantity = int(parts[2])
                                            target_agent_name = parts[3]
                                            target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                                            if target_agent:
                                                self.give_item(target, quantity, target_agent, environment)
                                            else:
                                                self.send_message(f"Agent {target_agent_name} not found.", environment)
                                        elif action == "ask" and len(parts) >= 4:
                                            quantity = int(parts[2])
                                            target_agent_name = parts[3]
                                            target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                                            if target_agent:
                                                self.ask_for_item(target, quantity, target_agent, environment)
                                            else:
                                                self.send_message(f"Agent {target_agent_name} not found.", environment)
                                        elif action == "trade" and len(parts) >= 6:
                                            quantity = int(parts[2])
                                            target_agent_name = parts[3]
                                            target_item = parts[4]
                                            target_quantity = int(parts[5])
                                            target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                                            if target_agent:
                                                self.trade_item(target, quantity, target_item, target_quantity, target_agent, environment)
                                            else:
                                                self.send_message(f"Agent {target_agent_name} not found.", environment)
                                        else:
                                            self.send_message("Invalid command. Please try again.", environment)
                                            self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)
                                    elif parts[0] == "inventory":
                                        self.list_inventory(environment)
                                    elif parts[0] == "help":
                                        self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)
                                    elif parts[0] == "think":
                                        self.think(environment)
                                    else:
                                        # Regular chat, no need to consider as a command
                                        pass
                          ''''
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
                        self.parse_command(command, environment)
            else:
                time.sleep(1)  # Wait for a short time before checking the next agent

            current_agent_index = (current_agent_index + 1) % len(turn_order)

    def extract_command(self, text):
        # Check if the text contains a valid command
        for command in self.memory.get("command_list", []):
            if command.split("{")[0].strip() in text.lower():
                return text
        return None


def generate_random_name():
    names = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry", "Isabella", "Jack",
             "Kate", "Liam", "Mia", "Nate", "Olivia", "Peter", "Quinn", "Ryan", "Sophia", "Tom"]
    return random.choice(names)


def generate_random_talent():
    talents = ["carpentry", "masonry", "electrical", "plumbing", "interior design"]
    return random.choice(talents)


def generate_random_trait():
    traits = ["helpful", "creative", "logical", "optimistic", "confident", "friendly", "patient", "resourceful", "determined", "curious"]
    return random.choice(traits)
def main():
    openai_base_url = "http://localhost:11434/v1"
    openai_api_key = "ollama"
    groq_api_key = "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"

    openai_api = OpenAI(base_url=openai_base_url, api_key=openai_api_key)
    groq_api = Groq(api_key=groq_api_key)

    environment = Environment()
    print("Environment has been created.")

    mayor_name = "Fred"
    mayor_api, mayor_model = random.choice([(openai_api, "mistral"), (groq_api, "mixtral-8x7b-32768")])
    mayor = Mayor(mayor_name, mayor_api, mayor_model)
    print(f"{mayor.name} has been appointed as the mayor.")

    num_agents = 5
    apis_and_models = [(openai_api, "mistral"), (groq_api, "mixtral-8x7b-32768")]

    for _ in range(num_agents):
        name = generate_random_name()
        talent = generate_random_talent()
        trait = generate_random_trait()
        api, model = random.choice(apis_and_models)
        agent = Agent(name, talent, trait, api, model)
        environment.add_agent(agent)

    print("Starting the town-building process...")
    environment.agents[0].build_town(environment)

    while True:
        mayor.provide_guidance(environment)
        time.sleep(1)  # Mayor checks for guidance every second

    print("Town-building process completed.")


if __name__ == "__main__":
    main()