import numpy as np
import matplotlib.pyplot as plt
import random
from collections import Counter

# System Parameters
GRID_SIZE = 100          
STEPS = 300000           
APATHY_START_RATIO = 0.05 
CANDIDATE_A_RATIO = 0.475 
CANDIDATE_B_RATIO = 0.475 

def initialize_grid(size, p_apath, p_a, p_b):
    choices = [0, 1, -1]
    probs = [p_apath, p_a, p_b]
    return np.random.choice(choices, size=(size, size), p=probs)

def run_simulation():
    grid = initialize_grid(GRID_SIZE, APATHY_START_RATIO, CANDIDATE_A_RATIO, CANDIDATE_B_RATIO)
    avalanche_sizes = []
    
    current_avalanche = 0
    quiet_steps = 0        
    NEWS_CYCLE_LIMIT = 15  # Inactivity threshold to terminate a cascade
    
    plt.ion()
    fig, ax = plt.subplots()
    img = ax.imshow(grid, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title("Opinion Dynamics: Avalanche Simulation")
    
    for step in range(STEPS):
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        current_state = grid[x, y]
        
        # Moore neighborhood evaluation
        neighbors = [
            grid[(x + 1) % GRID_SIZE, y], grid[(x - 1) % GRID_SIZE, y],
            grid[x, (y + 1) % GRID_SIZE], grid[x, (y - 1) % GRID_SIZE],
            grid[(x + 1) % GRID_SIZE, (y + 1) % GRID_SIZE], 
            grid[(x - 1) % GRID_SIZE, (y - 1) % GRID_SIZE], 
            grid[(x + 1) % GRID_SIZE, (y - 1) % GRID_SIZE], 
            grid[(x - 1) % GRID_SIZE, (y + 1) % GRID_SIZE]  
        ]
        
        count_A = neighbors.count(1)
        count_B = neighbors.count(-1)
        changed = False
        
        # State transition rules
        if current_state == 0:
            if count_A >= 3:
                grid[x, y] = 1
                changed = True
            elif count_B >= 3:
                grid[x, y] = -1
                changed = True
                
        elif current_state == 1:
            if count_B >= 5:
                grid[x, y] = -1
                changed = True
            elif count_B >= 2 and count_B >= count_A:
                 grid[x, y] = 0
                 changed = True
                 
        elif current_state == -1:
            if count_A >= 5:
                grid[x, y] = 1
                changed = True
            elif count_A >= 2 and count_A >= count_B:
                 grid[x, y] = 0
                 changed = True

        # Avalanche tracking
        if changed:
            current_avalanche += 1
            quiet_steps = 0 
        else:
            quiet_steps += 1
            if quiet_steps > NEWS_CYCLE_LIMIT: 
                if current_avalanche > 0:
                    avalanche_sizes.append(current_avalanche)
                    current_avalanche = 0
        
        if step % 5000 == 0:
            img.set_data(grid)
            plt.pause(0.01)

    plt.ioff()
    plt.close()
    
    if current_avalanche > 0:
        avalanche_sizes.append(current_avalanche)
        
    return avalanche_sizes

print(f"Initializing simulation ({STEPS} steps)...")
avalanches = run_simulation()

print(f"Simulation complete. Total avalanches recorded: {len(avalanches)}")

# Data processing and visualization
if len(avalanches) > 0:
    counts = Counter(avalanches)
    
    clean_sizes = []
    clean_freqs = []
    
    # Filter finite-size noise (single occurrences)
    for size, freq in counts.items():
        if freq > 1:
            clean_sizes.append(size)
            clean_freqs.append(freq)

    plt.figure()
    plt.scatter(clean_sizes, clean_freqs, color='black', marker='.')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Filtered Opinion Avalanche Distribution')
    plt.xlabel('Avalanche Size (Number of Flipped States)')
    plt.ylabel('Frequency P(s)')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    
    plt.savefig('avalanche_plot_clean.png', dpi=300, bbox_inches='tight')
    print("Output saved to 'avalanche_plot_clean.png'")
    
    plt.show()
else:
    print("No avalanches recorded.")
