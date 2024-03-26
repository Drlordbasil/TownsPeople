import pygame
from multiprocessing import Lock

def visualize_town(grid_size, shared_grid, shared_grid_lock):
    # Initialize Pygame
    pygame.init()

    # Set up the window size based on the grid size
    cell_size = 50
    window_width = grid_size[0] * cell_size
    window_height = grid_size[1] * cell_size
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Town Visualization")
    clock = pygame.time.Clock()

    # Set up colors
    background_color = (255, 255, 255)
    agent_color = (0, 0, 255)
    mayor_color = (255, 0, 0)

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill(background_color)

        # Draw the agents
        with shared_grid_lock:
            print("Acquiring shared_grid_lock...")
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    grid_value = shared_grid[i * grid_size[1] + j]
                    print(f"Grid value at ({i}, {j}): {grid_value}")
                    if grid_value == 1:
                        pygame.draw.circle(screen, agent_color, (i * cell_size + cell_size // 2, j * cell_size + cell_size // 2), cell_size // 4)
                        print(f"Agent drawn at ({i}, {j})")
                    elif grid_value == 2:
                        pygame.draw.circle(screen, mayor_color, (i * cell_size + cell_size // 2, j * cell_size + cell_size // 2), cell_size // 3)
                        print(f"Mayor drawn at ({i}, {j})")
            print("Releasing shared_grid_lock...")

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Limit the frame rate

    # Quit Pygame
    pygame.quit()