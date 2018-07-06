import networkx as nx
import pickle
import os
import community


class mention_network:

    def __init__(self, gexf_file, partition_resolution=0.3):
        # load network
        self.graph = nx.read_gexf(gexf_file)
        self.partition_resolution = partition_resolution
        # load all_paths_length
        self.all_paths_path = "bin/all_paths.bin"
        self.graph_copy = self.graph
        if os.path.exists(self.all_paths_path):
            self.all_paths = pickle.load(open(self.all_paths_path, mode='rb'))
        else:
            os.makedirs("bin")
            for edge in self.graph_copy.edges:
                self.graph_copy[edge[0]][edge[1]]['weight'] = 1
            self.all_paths = dict(
                nx.all_pairs_shortest_path_length(
                    self.graph_copy))
            pickle.dump(self.all_paths, open(self.all_paths_path, mode='wb'))

        # load partition
        self.partition_path = "bin/partition_per{}.bin".format(
            partition_resolution)
        self.graph_copy = self.graph
        if os.path.exists(self.partition_path):
            self.partition = pickle.load(open(self.partition_path, mode='rb'))
        else:
            for edge in self.graph_copy.edges:
                weight = self.graph_copy[edge[0]][edge[1]]['weight']
                self.graph_copy[edge[0]][edge[1]]['weight'] = 1 / weight
            self.graph_copy = nx.to_undirected(self.graph_copy)
            self.partition = community.best_partition(
                self.graph_copy, resolution=partition_resolution)
            pickle.dump(self.partition, open(self.partition_path, mode='wb'))

    def get_recommendations(self, uname='jnkka'):
        own_mentions = []
        close = []  # fof
        mid = []
        far = []

        # check the uname
        if uname not in self.all_paths:
            return []

        # close list - mentions of mentions
        for path in self.all_paths[uname]:
            if self.all_paths[uname][path] == 2:
                close.append(path)
            if self.all_paths[uname][path] < 2:  # 0 - self or 1 - mentions
                own_mentions.append(path)
        user_partition = self.partition[uname]

        # mid list - same partition
        for user in self.partition:
            valid = self.partition[user] == user_partition and user not in close and user not in own_mentions
            if valid:
                mid.append(user)

        # far list - rest of the users
        for user in self.partition:
            valid = user not in close and user not in mid and user not in own_mentions
            if valid:
                far.append(user)
        return {'direct': own_mentions, 'close': close, 'mid': mid, 'far': far}
