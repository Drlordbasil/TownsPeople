import time
import random
from multiprocessing import Process, Array, Lock
from openai import OpenAI
from groq import Groq
from environment import Environment
from mayor import Mayor
from agent import Agent
from utils import generate_random_name, generate_random_talent, generate_random_trait
from visualization import visualize_town

def main():
    openai_base_url = "http://localhost:11434/v1"
    openai_api_key = "ollama"
    groq_api_key = "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"

    openai_api = OpenAI(base_url=openai_base_url, api_key=openai_api_key)
    groq_api = Groq(api_key=groq_api_key)

    grid_size = (100, 100)
    environment = Environment(grid_size)
    print("Environment has been created.")

    mayor_name = "Fred"
    mayor_api, mayor_model = random.choice([(openai_api, "mistral")])
    mayor = Mayor(mayor_name, mayor_api, mayor_model)
    print(f"{mayor.name} has been appointed as the mayor.")

    num_agents = 5
    apis_and_models = [(openai_api, "mistral"),(openai_api, "llama2"),(openai_api, "gemma"), (groq_api, "mixtral-8x7b-32768"),(groq_api, "LLaMA2-70b"),(groq_api, "Gemma-7b-it")]

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
    #visualization_process = Process(target=visualize_town, args=(grid_size, shared_grid, shared_grid_lock))
    #visualization_process.start()

    # Start the build_town process
    environment.agents[0].build_town(environment, shared_grid, shared_grid_lock)

    # Wait for the build_town process to complete
    #visualization_process.join()

    print("Town-building process completed.")


if __name__ == "__main__":
    main()