import time

class NodeGraphAgent:
    def __init__(self):
        self.name = "Lab 7: Agentic Node Graph"
        self.graph_log = []

    def _execute_node(self, node_name, input_data):
        """Simulates a node executing its specific task."""
        print(f"  [Node: {node_name}] Processing input...")
        time.sleep(1) 
        
        if node_name == "Syllabus Node":
            # This node takes the request and outputs the topics
            output = f"Extracted Topics: [Docker, Kubernetes, Cloud Models]"
            
        elif node_name == "Question Selection Node":
            # This node takes the topics and outputs the selected questions
            output = f"Selected 3 questions matching the topics"
            
        elif node_name == "Formatting Node":
            # This node takes the selected questions and formats them
            output = f"Formatted paper with CO/PO tags and marks. Status: SUCCESS"
            
        else:
            output = "Unknown Node"
            
        print(f"  -> Output: {output}")
        self.graph_log.append({"node": node_name, "output": output})
        return output

    def run_graph(self, initial_request):
        print(f"\n[{self.name}] Starting Graph Execution...")
        print(f"Initial Request: {initial_request}")
        
        # Graph Edges: Output of Node 1 becomes Input of Node 2
        step1 = self._execute_node("Syllabus Node", initial_request)
        
        # We pass a simplified string so the log doesn't get messy
        step2 = self._execute_node("Question Selection Node", "Extracted Topics") 
        
        step3 = self._execute_node("Formatting Node", "Selected Questions")
        
        print(f"\n✅ [{self.name}] Graph Execution Complete.")
        return step3

if __name__ == "__main__":
    agent = NodeGraphAgent()
    agent.run_graph("Generate an ISA1 paper for Cloud Computing")