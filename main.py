import time
import random
from multiprocessing import Process, Array, Lock, Manager
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
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
import re

def extract_number(response):
    """
    Extracts the first integer found in the response string.

    Parameters:
    response (str): The response string from which to extract the number.

    Returns:
    int: The extracted number or None if no number is found.
    """
    match = re.search(r'\d+', response)
    if match:
        return int(match.group())
    return None

def main():
    console = Console()
    smart_model = "llama3"
    fast_model = "llama3"
    ollama_api = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

    # Create the environment
    grid_size = (30, 30)
    environment = Environment(grid_size)
    console.print(Panel(Text("Environment has been created.", style="bold green"), expand=False))

    # Create the mayor
    mayor_name = "Fred"
    mayor_api, mayor_model = random.choice([(ollama_api, smart_model)])
    mayor = Mayor(mayor_name, mayor_api, mayor_model)
    console.print(Panel(Text(f"{mayor.name} has been appointed as the mayor.", style="bold blue"), expand=False))

    # Create the agents
    num_agents = 3
    apis_and_models = [(ollama_api, fast_model), (ollama_api, smart_model), (ollama_api, fast_model)]
    agent_colors = [f"#{i:06x}" for i in range(num_agents)]  # Define colors for agents

    for i in range(num_agents):
        name = generate_random_name()
        talent = generate_random_talent()
        trait = generate_random_trait()
        api, model = random.choice(apis_and_models)
        agent = Agent(name, talent, trait, api, model)
        environment.add_agent(agent)
        agent_color = agent_colors[i]
        console.print(Panel(Text(f"Agent {agent.name} has been born with talent: {agent.talent} and trait: {agent.trait}.", style=Style(color=agent_color)), expand=False))

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

    console.print(Panel(Text("Starting the town-building process...", style="bold magenta"), expand=False))

    # Create a shared memory array to store the environment grid
    shared_grid_size = grid_size[0] * grid_size[1]
    shared_grid = Array('i', [0] * shared_grid_size)

    # Create a lock to synchronize access to the shared_grid
    shared_grid_lock = Lock()

    # Create a Manager for sharing messages
    manager = Manager()
    messages = manager.dict()

    # Start the visualization process
    visualization_process = Process(target=visualize_town, args=(grid_size, shared_grid, shared_grid_lock, messages))
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
                console.print(Panel(Text(f"Agent {current_agent.name} has determined that the town is complete.", style="bold green"), expand=False))
                is_town_complete = True
            else:
                command = current_agent.extract_command(response, environment)
                if command:
                    current_agent.parse_command(command, environment, shared_grid, shared_grid_lock)
                    state = current_agent.get_state(environment)
                    action = current_agent.choose_action(state)
                    reward = 0
                    if action == "trade":
                        prompt = "choose an item to trade"
                        item_to_trade_response = current_agent.generate_response(prompt, environment)
                        item_to_trade = current_agent.inventory.get_item_by_name(item_to_trade_response)
                        prompt = "choose an agent to trade with"
                        agent_to_trade_with_response = current_agent.generate_response(prompt, environment)
                        agent_to_trade_with = environment.get_agent_by_name(agent_to_trade_with_response)
                        trade_item(current_agent, agent_to_trade_with, item_to_trade.name)
                    elif action == "give":
                        prompt = "choose an item to give"
                        item_to_give_response = current_agent.generate_response(prompt, environment)
                        item_to_give = current_agent.inventory.get_item_by_name(item_to_give_response)
                        prompt = "choose an agent to give the item to"
                        agent_to_give_to_response = current_agent.generate_response(prompt, environment)
                        agent_to_give_to = environment.get_agent_by_name(agent_to_give_to_response)
                        give_item(current_agent, agent_to_give_to, item_to_give.name)
                    elif action == "ask":
                        prompt = "choose an item to ask for"
                        item_to_ask_for_response = current_agent.generate_response(prompt, environment)
                        item_to_ask_for = current_agent.inventory.get_item_by_name(item_to_ask_for_response)
                        prompt = "choose an agent to ask for the item"
                        agent_to_ask_response = current_agent.generate_response(prompt, environment)
                        agent_to_ask = environment.get_agent_by_name(agent_to_ask_response)
                        ask_for_item(current_agent, agent_to_ask, item_to_ask_for.name)
                    elif action == "update_inventory":
                        update_inventory(current_agent, environment)
                    elif action == "move":
                        prompt = "choose an x coordinate to move to (only reply with a number between 0 and 29)"
                        x_response = current_agent.generate_response(prompt, environment)
                        new_x = extract_number(x_response)
                        prompt = "choose a y coordinate to move to (only reply with a number between 0 and 29)"
                        y_response = current_agent.generate_response(prompt, environment)
                        new_y = extract_number(y_response)
                        if new_x is not None and new_y is not None:
                            move(current_agent, (new_x, new_y), environment, shared_grid, shared_grid_lock)
                        else:
                            console.print(Panel(Text(f"Invalid move command from {current_agent.name}.", style="bold red"), expand=False))
                    elif action == "use":
                        prompt = "choose an item to use"
                        item_to_use_response = current_agent.generate_response(prompt, environment)
                        item_to_use = current_agent.inventory.get_item_by_name(item_to_use_response)
                        use_item(current_agent, item_to_use.name, environment)
                    elif action == "put":
                        prompt = "choose an item to put in the environment"
                        item_to_put_response = current_agent.generate_response(prompt, environment)
                        item_to_put = current_agent.inventory.get_item_by_name(item_to_put_response)
                        environment.add_item(item_to_put, current_agent.position)

                    next_state = current_agent.get_state(environment)
                    current_agent.update_q_table(state, action, reward, next_state)
                    
                    # Update messages
                    agent_pos = current_agent.position
                    messages[agent_pos] = response
        else:
            console.print(Panel(Text(f"Agent {current_agent.name} failed to generate a response.", style="bold red"), expand=False))

        current_agent_index = (current_agent_index + 1) % len(turn_order)

        # Mayor provides guidance
        mayor.provide_guidance(environment)

    console.print(Panel(Text("Town-building process completed.", style="bold magenta"), expand=False))

    # Wait for the visualization process to complete
    visualization_process.join()

if __name__ == "__main__":
    main()
