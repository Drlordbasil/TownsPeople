import matplotlib.pyplot as plt
import matplotlib.animation as animation
from threading import Lock
import time
import numpy as np

def visualize_town(grid_size, shared_grid, shared_grid_lock, messages):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.set_xticks(np.arange(0, grid_size[0], 1))
    ax.set_yticks(np.arange(0, grid_size[1], 1))
    ax.grid(which="both")
    ax.set_aspect("equal")
    
    scatter = ax.scatter([], [], s=200, c=[])

    def update(frame):
        with shared_grid_lock:
            data = np.array(shared_grid).reshape(grid_size)
        agent_positions = np.argwhere(data == 1)
        mayor_positions = np.argwhere(data == 2)

        positions = np.vstack((agent_positions, mayor_positions))
        colors = ['blue'] * len(agent_positions) + ['red'] * len(mayor_positions)
        
        scatter.set_offsets(positions)
        scatter.set_color(colors)
        
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        ax.set_title(f"Current Time: {current_time}")

    ani = animation.FuncAnimation(fig, update, frames=200, interval=1000, repeat=False)
    plt.show()

