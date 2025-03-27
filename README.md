# Ms. Pacman AI Agents

This project demonstrates the implementation of various search algorithms to play the classic Ms. Pacman game using the Arcade Learning Environment (ALE). The agents implemented include:

- **Random Agent**: A baseline agent that selects actions randomly.
- **BFS Agent**: Uses Breadth-First Search to find paths to the nearest dots.
- **DFS Agent**: Uses Depth-First Search to explore paths.
- **A* Agent**: Uses A* search with heuristics to find optimal paths.

## Setup

### Prerequisites
- Python 3.10
- Virtual environment with the following packages:
  - `ale-py`
  - `numpy`
  - `autorom`

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pacman_search_ai
   ```

2. Create and activate a virtual environment:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install ale-py numpy autorom
   AutoROM --accept-license
   ```

## Running the Agents

To compare the performance of different agents, run the comparison script:
```bash
python compare_agents.py
```

This will execute each agent for a specified number of episodes and print a comparison of their performance, including average scores, frames, and time taken.

## Results

The results of the comparison are saved in `comparison_results.json` and printed in the terminal. The table includes:
- **Agent**: The name of the agent.
- **Avg Score**: The average score achieved by the agent.
- **Avg Frames**: The average number of frames per episode.
- **Avg Time**: The average time taken per episode.

## Future Work
- Implement additional heuristics for the A* agent.
- Develop a web interface to visualize and compare agent performance.
- Explore reinforcement learning approaches for dynamic strategy adaptation.

## License
This project is licensed under the MIT License. 