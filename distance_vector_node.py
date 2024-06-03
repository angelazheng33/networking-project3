from simulator.node import Node
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        self.outbound_links = {} # key: neighbor, value: [seq_num, cost]
        self.neighbors_dvs = {} # neighbor --> destination --> [cost, path]

        self.node_dv = {int(self.id): [0, []]} # key: destination, value: [cost, path]

        self.seq_num = 0

    # Return a string
    def __str__(self):
        return f"This is node {self.id} \n"

    def bellmanFord(self):
        # Initialization
        dist = {int(self.id): 0}
        node_path = {int(self.id): []}

        for neighbor in self.outbound_links:
            if neighbor not in self.neighbors_dvs:
                neighbor = int(neighbor)
                alt = self.outbound_links[neighbor][1]
                if neighbor not in dist or alt < dist[neighbor]:
                    dist[neighbor] = alt
                    node_path[neighbor] = [neighbor]
            else:
                neighbor = int(neighbor)
                for dst in self.neighbors_dvs[neighbor]:
                    path = [neighbor] + self.neighbors_dvs[neighbor][dst][1]
                    cost = self.neighbors_dvs[neighbor][dst][0] + self.outbound_links[neighbor][1]
                    if int(self.id) not in path:
                        dst = int(dst)
                        if dst not in dist or cost < dist[dst]:
                            dist[dst] = cost
                            node_path[dst] = path

        new_dv = {}

        for i in dist:
            new_dv[i] = [dist[i], node_path[i]]

        if self.node_dv != new_dv:
            self.node_dv = new_dv
            message = json.dumps([self.id, self.seq_num, self.node_dv])
            self.send_to_neighbors(message)
            self.seq_num += 1

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        neighbor = int(neighbor)

        if latency == -1:
            self.neighbors.remove(neighbor)
            self.neighbors_dvs.pop(neighbor)
            self.outbound_links.pop(neighbor)
        elif neighbor in self.neighbors:
            self.outbound_links[neighbor][1] = latency
        else:
            self.neighbors.append(neighbor)
            self.outbound_links[neighbor] = [-1, latency]

        self.bellmanFord()

    # Fill in this function
    def process_incoming_routing_message(self, m):
        message = json.loads(m)
        src = message[0]
        seq_num = message[1]
        dv = message[2]

        src = int(src)
        if src in self.outbound_links and seq_num > self.outbound_links[src][0]:
            self.outbound_links[src][0] = seq_num
            self.neighbors_dvs[src] = dv
            self.bellmanFord()

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        if int(destination) not in self.node_dv:
            return -1
        return int(self.node_dv[int(destination)][1][0])