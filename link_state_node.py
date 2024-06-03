from simulator.node import Node
import json

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.seq_num = 0
        self.table = {}
        self.done = False
        self.path = {id: []}

    # Return a string
    def __str__(self):
        return f"This is node {self.id} \n"
        # messages include link source, link destination, sequence number, link cost

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        # realizes change
        # constructs message to send to it's neighbors

        if latency == -1:
            if neighbor in self.neighbors:
                self.neighbors.remove(neighbor)
            latency = float("inf")

        elif neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            for (src, dst), val in self.table.items():
                message = json.dumps([src, dst, val[0], val[1]])
                self.send_to_neighbor(neighbor, message)

        # msg: <src, dst, seq, cost>
        # if latency != float("inf"):
        self.table[frozenset([self.id, neighbor])] = [self.seq_num, latency]
        broadcast_message = json.dumps([self.id, neighbor, self.table[frozenset([self.id, neighbor])][0], latency])
        self.send_to_neighbors(broadcast_message)
        self.done = True
        self.seq_num += 1

    # Fill in this function
    def process_incoming_routing_message(self, m):
        message = json.loads(m)
        link = frozenset([message[0], message[1]])
        seq_num = message[2]
        latency = message[3]

        if link not in self.table or seq_num > self.table[link][0]:
            self.table[link] = (seq_num, latency)
            self.send_to_neighbors(m)
            self.done = True

    # Return a neighbor, -1 if no path to destination
    def dijkstra(self):
        dist = {self.id: 0}
        curr_nodes = set()
        alt = float("inf")

        # getting each vertex in graph
        for (a, b), val in self.table.items():
            if val[1] != float("inf"):
                curr_nodes.add(a)
                curr_nodes.add(b)

        # Initialization
        for i in curr_nodes:
            if i != self.id:
                dist[i] = float("inf")
                self.path[i] = []

        # finds the nearest univisited node
        while curr_nodes:
            # find closest node
            shortest_dist = float("inf")
            closest_node = -1
            for node, lat in dist.items():
                if lat < shortest_dist and node in curr_nodes:
                    shortest_dist = lat
                    closest_node = node
            curr_nodes.remove(closest_node)

            for n in curr_nodes:
                if frozenset([closest_node, n]) in self.table and n in curr_nodes:
                    alt = dist[closest_node] + self.table[frozenset([closest_node, n])][1]
                    if dist[n] > alt:
                        dist[n] = alt
                        self.path[n] = self.path[closest_node] + [closest_node]


    def get_next_hop(self, destination):
        if self.done:
            self.dijkstra()
            self.done = False

        if destination not in self.path:
            return -1
        else:
            if len(self.path[destination]) > 1:
                return self.path[destination][1]
            return destination