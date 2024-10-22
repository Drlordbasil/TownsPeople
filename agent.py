import time
import random
from message import Message
from inventory import Inventory
from action import update_inventory, list_inventory, examine_item, use_item, give_item, ask_for_item, trade_item, accept_trade, move
from environment import Environment

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
        self.hunger = 100
        self.energy = 100
        self.skills = {
            "carpentry": 1,
            "masonry": 1,
            "electrical": 1,
            "plumbing": 1,
            "interior_design": 1
        }
        self.relationships = {}
        self.money = 100
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1

    def interact_with_agent(self, other_agent, environment):
        relationship = self.relationships.get(other_agent.name, 0)
        if relationship >= 50:
            self.send_message(f"Hey {other_agent.name}, how can I help you today?", environment)
        elif relationship <= -50:
            self.send_message(f"I don't have time for you, {other_agent.name}.", environment)
        else:
            self.send_message(f"Hello {other_agent.name}, what brings you here?", environment)

    def gain_experience(self, skill, amount):
        self.skills[skill] += amount
        print(f"Agent {self.name} gained {amount} experience in {skill}.")
        

    def learn_from_agent(self, other_agent, skill, environment):
        if self.skills[skill] < other_agent.skills[skill]:
            experience_gained = min(other_agent.skills[skill] - self.skills[skill], 10)
            self.gain_experience(skill, experience_gained)
            self.send_message(f"Thank you, {other_agent.name}, for teaching me about {skill}! I learned a lot.", environment)
        else:
            self.send_message(f"Thanks for the offer, {other_agent.name}, but I think I have a good grasp of {skill} for now.", environment)

    def receive_message(self, message):
        self.messages.append(message)

    def send_message(self, message_content, environment, is_announcement=False):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        message = Message(self.name, message_content, timestamp)
        nearby_agents = environment.get_nearby_agents(self.position)
        for agent in nearby_agents:
            if agent != self:
                agent.receive_message(message)
        if is_announcement:
            print(f"Mayor's Announcement: {message_content}")
        else:
            print(str(message))

    def generate_response(self, prompt, environment, role="user", max_retries=3, retry_delay=5):
        retries = 0
        while retries < max_retries:
            try:
                completion = self.api.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"You are {self.name} within {environment}, an agent who is {self.trait}. Respond naturally to the conversation, but if you want to perform an action, please use a valid command from the list of available commands. You will always have access to your inventory and the environment's items and will never loop back to the same prompt and always adapt for the town's good. Ask personal questions. Work together as a team, be a leader."},
                        {"role": role, "content": prompt}
                    ],
                    temperature=0.7,
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"Error generating response: {e}")
                retries += 1
                time.sleep(retry_delay)

        return None


    def think(self, environment):
        prompt = f"Analyze the current situation and your inventory. What should you do next to help build the town? Respond with your inner thoughts."
        inner_thoughts = self.generate_response(prompt, environment, role="assistant")
        if inner_thoughts:
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
                quantity = int(parts[1])
                target_agent_name = parts[3]
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    give_item(self, target, quantity, target_agent, environment)
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "ask" and len(parts) >= 5:
                target_agent_name = parts[1]
                quantity = int(parts[3])
                target = parts[4]
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    ask_for_item(self, target, quantity, target_agent, environment)
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "trade" and len(parts) >= 8:
                quantity = int(parts[1])
                item_name = parts[2]
                target_agent_name = parts[4]
                target_quantity = int(parts[6])
                target_item = parts[7]
                target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                if target_agent:
                    trade_item(self, item_name, quantity, target_item, target_quantity, target_agent, environment)
                else:
                    self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "accept" and len(parts) >= 3:
                if parts[1] == "trade":
                    target_agent_name = parts[3]
                    target_agent = next((agent for agent in environment.agents if agent.name == target_agent_name), None)
                    if target_agent:
                        trade_proposal = target_agent.memory.get(f"proposed_trade_with_{self.name}", None)
                        if trade_proposal:
                            item_name, quantity, target_item, target_quantity = trade_proposal
                            accept_trade(self, item_name, quantity, target_item, target_quantity, target_agent, environment)
                            del target_agent.memory[f"proposed_trade_with_{self.name}"]
                        else:
                            self.send_message(f"There is no pending trade proposal from {target_agent_name}.", environment)
                    else:
                        self.send_message(f"Agent {target_agent_name} not found.", environment)
            elif action == "move" and len(parts) >= 3:
                new_x = int(parts[1])
                new_y = int(parts[2])
                move(self, (new_x, new_y), environment, shared_grid, shared_grid_lock)
            else:
                self.send_message(environment.list_commands(), environment)
                self.think(environment)
        elif parts[0] == "inventory":
            list_inventory(self, environment)
        elif parts[0] == "help":
            self.send_message(environment.list_commands(), environment)
        elif parts[0] == "think":
            self.think(environment)
        else:
            self.think(environment)
            self.choose_action(environment)
            pass

    def get_state(self, environment):
        nearby_agents = environment.get_nearby_agents(self.position)
        state = (
            tuple(sorted(self.inventory.items)),
            tuple(sorted(agent.name for agent in nearby_agents)),
            self.position
        )
        return state

    def get_max_q(self, state):
        if state not in self.q_table:
            self.q_table[state] = {action: 0 for action in self.get_available_actions(state)}
        return max(self.q_table[state].values())

    def get_available_actions(self, state):
        actions = ["move", "trade", "give", "ask"]
        if self.inventory.items:
            actions.extend(["use", "put"])
        return actions

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.get_available_actions(state))
        else:
            if state not in self.q_table:
                self.q_table[state] = {action: 0 for action in self.get_available_actions(state)}
            return max(self.q_table[state], key=self.q_table[state].get)

    def update_q_table(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {action: 0 for action in self.get_available_actions(state)}
        old_value = self.q_table[state].get(action, 0)
        next_max = self.get_max_q(next_state)
        new_value = (1 - self.learning_rate) * old_value + self.learning_rate * (reward + self.discount_factor * next_max)
        self.q_table[state][action] = new_value

    def build_town(self, environment, shared_grid, shared_grid_lock):
        print(f"Agent {self.name} is initiating the town-building process.")
        self.send_message("Let's start building our new town together!", environment)
        self.send_message("""
        Discover the town's surroundings and gather resources to build the town, check everything in your town, make sure you build an economy with words.
        """, environment)

        self.send_message(environment.list_items(), environment)
        self.send_message(environment.list_commands(), environment)

        turn_order = environment.agents.copy()
        current_agent_index = 0
        is_town_complete = False

        while not is_town_complete:
            current_agent = turn_order[current_agent_index]
            prompt = "\n".join(str(message) for message in environment.messages[-5:])
            response = current_agent.generate_response(prompt, environment)
            if response:
                current_agent.send_message(response, environment)

                if "town is complete" in response.lower():
                    print(f"Agent {current_agent.name} has determined that the town is complete.")
                    is_town_complete = True
                else:
                    command = current_agent.extract_command(response, environment)
                    if command:
                        current_agent.parse_command(command, environment, shared_grid, shared_grid_lock)
                        state = current_agent.get_state(environment)
                        action = current_agent.choose_action(state)
                        reward = 0
                        if action == "trade":
                            nearby_agents = environment.get_nearby_agents(current_agent.position)
                            if nearby_agents:
                                other_agents = [agent for agent in nearby_agents if agent != current_agent]
                                if other_agents:
                                    target_agent = random.choice(other_agents)
                                    if target_agent and target_agent.inventory.items:
                                        item_to_give = random.choice(current_agent.inventory.items)
                                        item_to_receive = random.choice(target_agent.inventory.items)
                                        trade_item(current_agent, item_to_give.name, item_to_give.quantity, item_to_receive.name, item_to_receive.quantity, target_agent, environment)
                                        reward = 10
                        elif action == "give":
                            nearby_agents = environment.get_nearby_agents(current_agent.position)
                            if nearby_agents:
                                target_agents = [agent for agent in nearby_agents if agent != current_agent]
                                if target_agents:
                                    target_agent = random.choice(target_agents)
                                    item_to_give = random.choice(current_agent.inventory.items)
                                    give_item(current_agent, item_to_give.name, item_to_give.quantity, target_agent, environment)
                                    reward = 5
                        elif action == "ask":
                            nearby_agents = environment.get_nearby_agents(current_agent.position)
                            if nearby_agents:
                                target_agents = [agent for agent in nearby_agents if agent != current_agent and agent.inventory.items]
                                if target_agents:
                                    target_agent = random.choice(target_agents)
                                    item_to_ask = random.choice(target_agent.inventory.items)
                                    ask_for_item(current_agent, item_to_ask.name, item_to_ask.quantity, target_agent, environment)
                                    reward = 2
                        elif action == "move":
                            new_x = random.randint(0, environment.grid_size[0] - 1)
                            new_y = random.randint(0, environment.grid_size[1] - 1)
                            move(current_agent, (new_x, new_y), environment, shared_grid, shared_grid_lock)
                        elif action == "use":
                            item_to_use = random.choice(current_agent.inventory.items)
                            use_item(current_agent, item_to_use.name, environment)
                        elif action == "put":
                            item_to_put = random.choice(current_agent.inventory.items)
                            update_inventory(current_agent, item_to_put.name, item_to_put.quantity, environment, "put")

                        next_state = current_agent.get_state(environment)
                        current_agent.update_q_table(state, action, reward, next_state)
            else:
                print(f"Agent {current_agent.name} failed to generate a response.")

            current_agent_index = (current_agent_index + 1) % len(turn_order)

            try:
                user_input = input("Enter your suggestion or announcement (or 'q' to quit): ")
                if user_input.lower() == 'q':
                    is_town_complete = True
                    break
                elif user_input:
                    current_agent.send_message(user_input, environment, is_announcement=True)
            except:
                pass

        print("Town-building process completed.")

    def extract_command(self, text, environment):
        command_list = environment.commands
        for command in command_list:
            if command.split("{")[0].strip() in text.lower():
                return text
        return None
