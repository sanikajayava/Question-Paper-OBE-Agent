import time

class NodeGraphAgent:
    def __init__(self):
        self.name = "Lab 7: Agentic Node Graph"
        self.graph_log = []

    def _execute_node(self, node_name, input_data):
        """Simulates a node executing its specific task."""
        print(f"  [Node: {node_name}] Processing input...")
        time.sleep(1) # Simulate processing time
        
        # Logic for each node (Output of one becomes Input of next)
        if node_name == "Requirements Node":
            output = f"Analyzed '{input_data}'. Extracted: [Login, Dashboard, DB]"
            
        elif node_name == "Design Node":
            output = f"Designed architecture for {input_data}. Output: [React, Python]"
            
        elif node_name == "Release Node":
            output = f"Deployed {input_data} to Cloud. Status: SUCCESS"
            
        else:
            output = "Unknown Node"
            
        print(f"  -> Output: {output}")
        self.graph_log.append({"node": node_name, "output": output})
        return output

    def run_graph(self, initial_request):
        print(f"\n[{self.name}] Starting Graph Execution...")
        print(f"Initial Request: {initial_request}")
        
        # Graph Edges (Connections): Pass output of node 1 into node 2, etc.
        step1 = self._execute_node("Requirements Node", initial_request)
        step2 = self._execute_node("Design Node", step1)
        step3 = self._execute_node("Release Node", step2)
        
        print(f"\n✅ [{self.name}] Graph Execution Complete.")
        return step3

if __name__ == "__main__":
    agent = NodeGraphAgent()
    agent.run_graph("Build a new Campus App for students")