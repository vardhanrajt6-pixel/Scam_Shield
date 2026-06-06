import networkx as nx

class ScamGraph:
    def __init__(self):
        # Initialize empty undirected graph
        self.graph = nx.Graph()

        # --- Seed graph with known scam examples ---
        self._seed_graph()

    def _seed_graph(self):
        """
        Add a few known scam examples at startup so similarity checks
        can trigger immediately.
        """
        scam_examples = [
            "Your account will be blocked unless you verify now",
            "Click here to claim your prize",
            "Urgent: update your bank details immediately",
            "Congratulations! You have won a lottery, send your info",
            "Verify your password to avoid suspension"
        ]
        for msg in scam_examples:
            self.add_message(msg, "scam")

    def add_message(self, message: str, label: str):
        """
        Add a message node to the graph.
        Nodes represent messages or keywords.
        """
        if message not in self.graph:
            self.graph.add_node(message, label=label)
        else:
            # Update label if node already exists
            self.graph.nodes[message]["label"] = label

    def add_relationship(self, msg1: str, msg2: str, similarity: float):
        """
        Add an edge between two messages if similarity is high.
        """
        if msg1 != msg2:
            self.graph.add_edge(msg1, msg2, weight=similarity)

    def get_graph(self):
        return self.graph
