import numpy as np


class Refex:
    def __init__(self):
        self.graph = {}
        self.p = 0.5
        self.s = 0
        self.refex_log_binned_buckets = {}

    def load_graph(self, file_name):
        source = 0
        for line in open(file_name):
            line = line.strip()
            line = line.split()
            for dest in line:
                dest = int(dest)
                if source not in self.graph:
                    self.graph[source] = [dest]
                else:
                    self.graph[source].append(dest)
                if dest not in self.graph:
                    self.graph[dest] = [source]
                else:
                    self.graph[dest].append(source)
            source += 1
        for key in self.graph.keys():
            self.graph[key] = list(set(self.graph[key]))

    def get_number_of_vertices(self):
        return len(self.graph)

    def get_degree_of_vertex(self, vertex):
        return len(self.graph[vertex])

    def get_egonet_degree(self, vertex):
        adjacency_list = self.graph[vertex]
        return sum([self.get_degree_of_vertex(v) for v in adjacency_list])

    def get_egonet_members(self, vertex):
        return self.graph[vertex]

    def get_count_of_edges_leaving_egonet(self, vertex):
        edges_leaving_egonet = 0
        egonet = self.get_egonet_members(vertex)
        for vertex in egonet:
            for neighbour in self.get_egonet_members(vertex):
                if neighbour not in egonet:
                    edges_leaving_egonet += 1
        return edges_leaving_egonet

    def get_count_of_within_egonet_edges(self, vertex):
        within_egonet_edges = 0
        egonet = self.get_egonet_members(vertex)
        for vertex in egonet:
            for neighbour in self.get_egonet_members(vertex):
                if neighbour in egonet:
                    within_egonet_edges += 1
        return within_egonet_edges / 2

    def compute_recursive_features(self, features):
        vertex_fx_vector = {}
        no_vertices = self.get_number_of_vertices()
        for k in xrange(0, no_vertices):
            vertex_fx_vector[k] = []

        for feature in features.keys():
            feature_values = features[feature]  # assuming list of 2-tuples
            sorted_fx_values = sorted(feature_values, key=lambda x: x[1])
            sorted_fx_values_size = len(sorted_fx_values)

            count_of_vertices_with_log_binned_fx_value = 0

            for log_binned_fx_value in sorted(self.refex_log_binned_buckets.keys()):
                if no_vertices == count_of_vertices_with_log_binned_fx_value:
                    # case when all vertices have been already binned owing to ties/collision
                    break

                no_vertices_in_current_log_binned_bucket = self.refex_log_binned_buckets[log_binned_fx_value]

                fx_value_of_last_vertex_to_be_taken = sorted_fx_values[count_of_vertices_with_log_binned_fx_value +
                                                                       no_vertices_in_current_log_binned_bucket - 1][1]
                # If there are ties, it may be necessary to include more than p|V| nodes
                for idx in xrange(count_of_vertices_with_log_binned_fx_value +
                                  no_vertices_in_current_log_binned_bucket, sorted_fx_values_size):
                    if sorted_fx_values[idx][1] == fx_value_of_last_vertex_to_be_taken:
                        no_vertices_in_current_log_binned_bucket += 1
                    else:
                        break

                for idx in xrange(count_of_vertices_with_log_binned_fx_value,
                                  count_of_vertices_with_log_binned_fx_value +
                                  no_vertices_in_current_log_binned_bucket):
                    vertex_no = sorted_fx_values[idx][0]
                    vertex_fx_vector[vertex_no].append(log_binned_fx_value)  # assign log binned value to vertex

                count_of_vertices_with_log_binned_fx_value += no_vertices_in_current_log_binned_bucket

        return vertex_fx_vector

    def init_log_binned_fx_buckets(self):
        no_vertices = self.get_number_of_vertices()
        max_fx_value = np.ceil(np.log2(no_vertices))  # fixing value of p = 0.5,
        # In our experiments, we found p = 0.5 to be a sensible choice:
        # with each bin containing the bottom half of the remaining nodes.
        log_binned_fx_keys = [value for value in xrange(0, int(max_fx_value))]

        fx_bucket_size = []
        starting_bucket_size = no_vertices

        for idx in np.arange(0.0, max_fx_value):
            starting_bucket_size *= self.p
            fx_bucket_size.append(int(np.ceil(starting_bucket_size)))

        total_slots_in_all_buckets = sum(fx_bucket_size)
        if total_slots_in_all_buckets > no_vertices:
            fx_bucket_size[0] -= (total_slots_in_all_buckets - no_vertices)

        self.refex_log_binned_buckets =  dict(zip(log_binned_fx_keys, fx_bucket_size))

