# decision tree algorithm using bottom up approach

# (parent, child)
class BUTreeAlgorithm:
    def __init__(self, training_data: [(str, str)]):
        self.training_data: [(str, str)] = training_data

    def prune_tree(self, branch: (str, str)):
        self.training_data.remove(branch)

    def prune_leaf(self, leaf: str):
        # leaf in self.leaf_nodes and
        branches = self.find_branches_of_leaf(leaf)
        leafs = self.find_link_of_leaf(leaf)
        if len(branches) > 0 or len(self.find_link_of_leaf(leaf)) > 0:
            # remove leaf as a parent
            for i in branches:
                if i[0] not in self.leaf_nodes and not self.is_isolated(i[0]):
                    print('isolating:', i[1])
                    self.isolate_leaf(i[1])
                    print('removing branch link:', i)
                    self.training_data.remove(i)
            # remove leaf as a child
            print(f'self.find_link_of_leaf({leaf})', leafs)
            for i in leafs:
                print('removing leaf link:', i)
                self.training_data.remove(i)
                if i[0] not in self.leaf_nodes and not self.is_isolated(i[0]):
                    print('isolating:', i[0])
                    self.isolate_leaf(i[0])

    # if len(self.find_link_of_leaf(leaf)) > 0:
    #     print(f'self.find_link_of_leaf({leaf})', self.find_link_of_leaf(leaf))
    #     for i in self.find_link_of_leaf(leaf):
    #         print('removing:', i)
    #         if i[1] not in self.leaf_nodes and not self.is_isolated(i[1]):
    #             print('isolating:', i[1])
    #             self.isolate_leaf(i[1])
    #         self.training_data.remove(i)

    def find_branches_of_leaf(self, leaf: str):
        return [i for i in self.training_data if i[0] == leaf]

    def find_link_of_leaf(self, leaf: str):
        return [i for i in self.training_data if i[1] == leaf]

    def isolate_leaf(self, leaf: str):
        self.training_data.append(('', leaf))

    def is_isolated(self, leaf: str):
        return leaf in self.isolated_leafs or leaf == ''

    @property
    def isolated_leafs(self):
        return [i[1] for i in self.training_data if i[0] == '']

    @property
    def leaf_nodes(self):
        parent_nodes = [i[0] for i in self.training_data]
        child_nodes = [i[1] for i in self.training_data]
        difference = list(set(child_nodes).difference(set(parent_nodes)))
        return [i[1] for i in self.training_data if i[1] in difference]


if __name__ == '__main__':
    data = [
        ('a', 'b'),
        ('b', 'c'),
        ('c', 'd'),
        ('d', 'e'),
        ('d', 'f'),
        ('f', 'g'),
    ]

    tree = BUTreeAlgorithm(data)
    print('initial tree.data', tree.training_data)
    tree.prune_leaf('a')
    print('tree.leaf_nodes 1', tree.leaf_nodes)
    tree.prune_leaf('a')
    print('tree.leaf_nodes 2', tree.leaf_nodes)
    tree.prune_leaf('g')
    print('tree.leaf_nodes 3', tree.leaf_nodes)
    print('tree.data', tree.training_data)
