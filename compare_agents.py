import os

# List of layouts to test
layouts = ['testClassic','originalClassic']  # Add more layouts as needed

# Agents to compare
agents = [
    ('SearchAgent', 'bfs'),
    ('ImprovedBFSAgent', None)
]

# Run each agent on each layout
for layout in layouts:
    for agent, fn in agents:
        command = f"python pacman.py -p {agent} -l {layout}"
        if fn:
            command += f" -a fn={fn}"
        print(f"Running: {command}")
        os.system(command)