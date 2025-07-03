import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fluid Simulation")

# Particle settings
particles = []
max_particles = 100
radius = 5
gravity = np.array([0,0.1])

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)

clock = pygame.time.Clock()

# # Matplotlib setup
# fig, ax = plt.subplots(figsize=(6, 4))
# ax.set_xlim(0, width)
# ax.set_ylim(height, 0)  # Invert y-axis to match Pygame
# ax.set_title("AVERAGE PARTICLE POSITION")
# line, = ax.plot([], [], 'ro-')
# average_positions = []  # ✅ Fixed typo here

# Function to add a new particle at the mouse position
def add_particle(pos):
    if len(particles) < max_particles:
        particles.append({
            'pos': np.array(pos, dtype=float),
            'vel': np.random.randn(2) * 2  # ✅ Changed 'neg' to 'vel'
        })

# Function to update all particle positions
def update_particles():
    for p in particles:
        p['vel']+=gravity
        p['pos'] += p['vel']

        # Bounce off walls
        if p['pos'][0] <= 0 or p['pos'][0] >= width:
            p['vel'][0] *= -1
        if p['pos'][1] <= 0 or p['pos'][1] >= height:
            p['vel'][1] *= -0.8  # Lose 20% of speed on bounce(damping)
            p['pos'][1] = height  # Keep inside screen
        
         # ✅ Handle collisions between particles
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            p1 = particles[i]
            p2 = particles[j]

            pos1 = p1['pos']
            pos2 = p2['pos']
            dist = np.linalg.norm(pos1 - pos2)

            if dist < 2 * radius:
                # Particles are overlapping → collision
                # Calculate the unit normal and unit tangent vectors
                normal = (pos2 - pos1) / dist
                tangent = np.array([-normal[1], normal[0]])

                # Project velocities onto normal and tangent
                v1n = np.dot(p1['vel'], normal)
                v1t = np.dot(p1['vel'], tangent)
                v2n = np.dot(p2['vel'], normal)
                v2t = np.dot(p2['vel'], tangent)

                # Swap normal components (elastic collision)
                v1n, v2n = v2n, v1n

                # Convert scalar normal and tangential velocities into vectors
                p1['vel'] = v1n * normal + v1t * tangent
                p2['vel'] = v2n * normal + v2t * tangent

                # Prevent sticking by moving particles apart
                overlap = 2 * radius - dist
                correction = normal * (overlap / 2)
                p1['pos'] -= correction
                p2['pos'] += correction

        
        


# Function to update the Matplotlib plot
# def update_plot(frame):
#     if particles:
#         avg_pos = np.mean([p['pos'] for p in particles], axis=0)
#         average_positions.append(avg_pos)
#         x_data = [pos[0] for pos in average_positions]
#         y_data = [pos[1] for pos in average_positions]
#         line.set_data(x_data, y_data)
#         ax.relim()
#         ax.autoscale_view()
#     return line,
# #setup animation
# anim = FuncAnimation(fig,update_plot, frames=8, interval = 10 ,blit = True)
# plt.show(block = False)

running = True  

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            add_particle(pygame.mouse.get_pos())
    
    update_particles()

    screen.fill(BLACK)

    #Draw particle
    for p in particles:
        pygame.draw.circle(screen, RED, p['pos'].astype(int),radius)
    pygame.display.flip()
    clock.tick(60)
    #update matplot
    plt.pause(0.001)

pygame.quit()
# plt.close(fig)