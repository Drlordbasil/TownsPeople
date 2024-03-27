import time
import random
from multiprocessing import Process, Array, Lock
from openai import OpenAI
from environment import Environment
from mayor import Mayor
from agent import Agent
from utils import generate_random_name, generate_random_talent, generate_random_trait
from visualization import visualize_town
from action import trade_item, give_item, ask_for_item, move, use_item, update_inventory
from message import Message
import logging
import os




def main():

    smart_model = "mistral"
    fast_model = "stablelm2"
    openai_api = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    # Create the environment
    grid_size = (30, 30)
    environment = Environment(grid_size)
    print("Environment has been created.")

    # Create the mayor
    mayor_name = "Fred"
    mayor_api, mayor_model = random.choice([(openai_api, smart_model)])
    mayor = Mayor(mayor_name, mayor_api, mayor_model)
    print(f"{mayor.name} has been appointed as the mayor.")

    # Create the agents
    num_agents = 20
    apis_and_models = [(openai_api, fast_model), (openai_api, smart_model), (openai_api, fast_model)]

    for _ in range(num_agents):
        name = generate_random_name()
        talent = generate_random_talent()
        trait = generate_random_trait()
        api, model = random.choice(apis_and_models)
        agent = Agent(name, talent, trait, api, model)
        environment.add_agent(agent)

    # Set initial positions for agents and mayor
    for agent in environment.agents:
        x, y = random.randint(0, grid_size[0] - 1), random.randint(0, grid_size[1] - 1)
        while not environment.is_valid_position((x, y)):
            x, y = random.randint(0, grid_size[0] - 1), random.randint(0, grid_size[1] - 1)
        environment.update_agent_position(agent, (x, y))

    mayor_x, mayor_y = random.randint(0, grid_size[0] - 1), random.randint(0, grid_size[1] - 1)
    while not environment.is_valid_position((mayor_x, mayor_y)):
        mayor_x, mayor_y = random.randint(0, grid_size[0] - 1), random.randint(0, grid_size[1] - 1)
    mayor.position = (mayor_x, mayor_y)

    print("Starting the town-building process...")

    # Create a shared memory array to store the environment grid
    shared_grid_size = grid_size[0] * grid_size[1]
    shared_grid = Array('i', [0] * shared_grid_size)

    # Create a lock to synchronize access to the shared_grid
    shared_grid_lock = Lock()

    # Start the visualization process
    visualization_process = Process(target=visualize_town, args=(grid_size, shared_grid, shared_grid_lock))
    visualization_process.start()

    # Start the town-building process
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



        # Mayor provides guidance
        mayor.provide_guidance(environment)

    print("Town-building process completed.")

    # Wait for the visualization process to complete
    visualization_process.join()

if __name__ == "__main__":
    main()