from bfs_agent import BFSAgent
from dfs_agent import DFSAgent
from astar_agent import AStarAgent
from pacman_agents import RandomAgent
import json
import time
from pathlib import Path

def run_comparison(episodes=3, save_results=True):
    """Compare different agents on Ms. Pacman."""
    agents = {
        "Random": RandomAgent(),
        "BFS": BFSAgent(),
        "DFS": DFSAgent(),
        "A*": AStarAgent()
    }
    
    rom_path = "venv/lib/python3.10/site-packages/ale_py/roms/ms_pacman.bin"
    results = {}
    
    for agent_name, agent in agents.items():
        print(f"\n🤖 Testing {agent_name} Agent...")
        agent_results = []
        
        try:
            agent.load_rom(rom_path)
            
            for episode in range(episodes):
                print(f"\n🎯 Episode {episode + 1}")
                start_time = time.time()
                metrics = agent.run_episode()
                end_time = time.time()
                
                episode_data = {
                    "episode": episode + 1,
                    "score": metrics["total_reward"],
                    "frames": metrics["total_frames"],
                    "time": round(end_time - start_time, 2)
                }
                agent_results.append(episode_data)
                
                print(f"🏁 Score: {metrics['total_reward']} | Frames: {metrics['total_frames']}")
            
            results[agent_name] = {
                "episodes": agent_results,
                "avg_score": sum(ep["score"] for ep in agent_results) / episodes,
                "avg_frames": sum(ep["frames"] for ep in agent_results) / episodes,
                "avg_time": sum(ep["time"] for ep in agent_results) / episodes
            }
            
        except Exception as e:
            print(f"❌ Error testing {agent_name} agent: {e}")
            results[agent_name] = {"error": str(e)}
    
    # Print comparison
    print("\n📊 Results Comparison:")
    print("=" * 50)
    print(f"{'Agent':<10} {'Avg Score':<12} {'Avg Frames':<12} {'Avg Time':<10}")
    print("-" * 50)
    
    for agent_name, data in results.items():
        if "error" not in data:
            print(f"{agent_name:<10} {data['avg_score']:<12.1f} {data['avg_frames']:<12.1f} {data['avg_time']:<10.2f}")
    
    if save_results:
        # Save results to file
        output_file = Path("comparison_results.json")
        with output_file.open("w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {output_file}")
    
    return results

if __name__ == "__main__":
    print("🎮 Starting Ms. Pacman Agent Comparison...")
    results = run_comparison() 