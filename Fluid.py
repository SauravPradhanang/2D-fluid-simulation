import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fluid Simulation")

# Particle settings
particles = []               # ✅ Initialize BEFORE spawning
max_particles = 100          # ✅ Initialize BEFORE spawning
radius = 5
gravity = np.array([0, 0.1])

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)

clock = pygame.time.Clock()

# Function to spawn all particles at the start
def spawn_particles_at_start():
    for _ in range(max_particles):
        pos = np.random.rand(2) * np.array([width, height])
        vel = (np.random.rand(2) - 0.5) * 10  # Random velocity between -5 and 5
        particles.append({
            'pos': pos,
            'vel': vel
        })

spawn_particles_at_start()   # ✅ Now runs correctly since variables are defined

# Update particle positions and handle collisions
def update_particles():
    for p in particles:
        p['vel'] += gravity
        p['pos'] += p['vel']

        # Wall collisions
        if p['pos'][0] <= 0 or p['pos'][0] >= width:
            p['vel'][0] *= -1
        if p['pos'][1] <= 0:
            p['vel'][1] *= -0.8
            p['pos'][1] = 0
        elif p['pos'][1] >= height:
            p['vel'][1] *= -0.8
            p['pos'][1] = height

    # Particle-particle collisions
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            p1 = particles[i]
            p2 = particles[j]
            pos1 = p1['pos']
            pos2 = p2['pos']
            dist = np.linalg.norm(pos1 - pos2)

            if dist < 2 * radius and dist != 0:
                normal = (pos2 - pos1) / dist
                tangent = np.array([-normal[1], normal[0]])

                v1n = np.dot(p1['vel'], normal)
                v1t = np.dot(p1['vel'], tangent)
                v2n = np.dot(p2['vel'], normal)
                v2t = np.dot(p2['vel'], tangent)

                # Swap normal components for elastic collision
                v1n, v2n = v2n, v1n

                p1['vel'] = v1n * normal + v1t * tangent
                p2['vel'] = v2n * normal + v2t * tangent

                # Separate particles to prevent sticking
                overlap = 2 * radius - dist
                correction = normal * (overlap / 2)
                p1['pos'] -= correction
                p2['pos'] += correction

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_particles()

    screen.fill(BLACK)

    for p in particles:
        pygame.draw.circle(screen, RED, p['pos'].astype(int), radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
