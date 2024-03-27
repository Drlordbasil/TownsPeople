import pygame
import time

def visualize_town(grid_size, shared_grid, shared_grid_lock):
    # Initialize Pygame
    pygame.init()

    # Set up the window size based on the grid size
    cell_size = 20
    window_width = grid_size[0] * cell_size
    window_height = grid_size[1] * cell_size
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Town Visualization")
    clock = pygame.time.Clock()

    # Set up colors
    background_color = (255, 255, 255)
    agent_color = (0, 0, 255)
    mayor_color = (255, 0, 0)
    
    # Set up font
    font = pygame.font.Font(None, 24)

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill(background_color)

        # Draw the grid lines
        for x in range(0, window_width, cell_size):
            pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, window_height))
        for y in range(0, window_height, cell_size):
            pygame.draw.line(screen, (200, 200, 200), (0, y), (window_width, y))

        # Draw the agents and mayor
        with shared_grid_lock:
            for i in range(grid_size[0]):
                for j in range(grid_size[1]):
                    cell_value = shared_grid[i * grid_size[1] + j]
                    if cell_value == 1:  # Agent
                        pygame.draw.circle(screen, agent_color, (i * cell_size + cell_size // 2, j * cell_size + cell_size // 2), cell_size // 2 - 2)
                    elif cell_value == 2:  # Mayor
                        pygame.draw.circle(screen, mayor_color, (i * cell_size + cell_size // 2, j * cell_size + cell_size // 2), cell_size // 2 - 2)

        # Display the current time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        time_text = font.render(current_time, True, (0, 0, 0))
        screen.blit(time_text, (10, 10))

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Limit the frame rate to 60 FPS

    # Quit Pygame
    pygame.quit()