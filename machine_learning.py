from computational_mathmatics import Node, Graph
from optim import Optim, Cost
import numpy as np


# special class of node, most basic machine learning node type
class Perceptron(Node):
    def __init__(self, variables, bias=0.1):
        super(Perceptron, self).__init__(variables)
        self.type = "perceptron"

    def eval(self, inputs: np.array, weights, bias):
        return np.dot(weights, inputs) + bias

    def activation(self, sum):
        return 0 if sum <= 0 else 1, self.next_nodes


class Sigmoid(Node):
    def __init__(self, variables):
        super(Sigmoid, self).__init__(variables)
        self.type = "sigmoid"

    # Overrides function method with sigmoid function

    def eval(self, inputs: np.array, weights, bias):
        return np.dot(weights, inputs) + bias

    def activation(self, z):
        eval = 1/(1 + np.exp(-z))
        return eval

    def derivative(self, z):
        return self.activation(z)*(1 - self.activation(z))

# will likely never be used
class Input(Node):
    def __init__(self, variables):
        super(Input, self).__init__(variables)
        self.type = "input"

    def eval(self, inputs: np.array, weights, bias):
        return np.dot(weights, inputs) + bias

    def activation(self, z):
        return z

    def derivative(self, z):
        return 1

# consider creating rather than different node types, different layer types??
class Layer:
    """
    Layer is made up of nodes, either fully connected or not.
    idea of operation is to go by layer and each layer will preform and store the values from each node
    which is passed onto the next layer etc.
    The layer will all operate on the same activation function. Or series of activation functions.
    Specify width of layers, whether it is fully connected or not.
    When adding the next layer to the model, connect each node based on whether it is fully connected or not.
    """

    def __init__(self, width, node=None, input_layer=False, fully_connected=True):
        self.width = width
        self.fully_connected = fully_connected
        # if input_layer:
        #     self.node = Input
        # else:
        self.node = node
        self.nodes = []
        # changed from v0.0.0 #
        self.weights = np.array([])
        # if input_layer:
        #     self.bias = np.zeros(width)
        # else:
        self.bias = np.random.randn(width)
        # last part for emphasis #
        self.next_layer = None
        self.prev_layer = None
        self.input_layer = input_layer

    # added in v 0.0.1
    def initialize_weights(self, prev_nodes=None):
        """
        :param prev_nodes: The node that comes before is optional only if the layer is thw input layer
        :return: This function initializes the weights for each node in a layer based on the the width of the previous
        node or if it is the input, itself
        """
        # ignore this for now, I'm going to try doing backprop on input layer too
        # input layer will just purely take in inputs, contemplate forcing input to be a generic layer
        if self.input_layer:
            print("input layer")
            self.weights = np.random.randn(self.width, self.width)
            # self.weights = np.ones(self.width, self.width)
        else:
            print("not input layer")
            assert prev_nodes
            self.weights = np.random.randn(self.width, prev_nodes)

    def initialize_layer(self, variables=None):
        if not variables:
            variables = self.width
            # if the user wishes to specify a type of node to use this is where it'll be done
        for i in range(self.width):
            self.nodes.append(self.node(variables))

    def connect(self, layer):
        self.next_layer = layer
        layer.prev_layer = self
        for node in layer.nodes:
            node.connect(self.nodes)
        layer.initialize_weights(self.width)

    def forward(self, inputs):
        if self.prev_layer:
            if self.prev_layer.width == 1:
                pass
            else:
                assert(inputs.size == self.prev_layer.width)
        else:
            assert (inputs.size == self.width)
        values = np.array([])
        zs = np.array([])
        for i in range(len(self.nodes)):
            # evaluates the node based on the node type or the function specified
            # might have to change depending if other models require different parameters to evaluate
            z = self.nodes[i].eval(inputs, self.weights[i], self.bias[i])
            val = self.nodes[i].activation(z)
            zs = np.append(zs, z)
            values = np.append(values, val)

        # function return the raw calculations to avoid repetition in back propogation
        return values, zs

    def definition(self):
        print(f"Width: {self.width}, Function: {self.node}, Fully Connected:"
              f" {self.fully_connected}, Sample Node: {self.nodes[0].node_def()}")


class Model:
    def __init__(self, layers: list, cost: Cost):
        self.layers = layers
        self.depth = len(layers)
        self.initialize_layers()
        self.optim = Optim(self, cost)
        for i in range(0, self.depth - 1):
            self.layers[i].connect(self.layers[i+1])

    def init_input(self):
        self.layers[0].prev_layer = None
        self.input_layer = self.layers[0]
        self.layers[0].initialize_layer()
        # below used to initialize the weights for itself
        self.layers[0].input_layer = True
        self.layers[0].initialize_weights()

    def init_output(self):
        self.layers[-1].next_layer = None
        self.output_layer = self.layers[-1]

    def initialize_layers(self):
        self.init_input()
        self.init_output()
        for i in range(1, len(self.layers), 1):
            self.layers[i].initialize_layer(self.layers[i - 1].width)

    # moves through each input and passes it through each node,
    # these values are then stored and passed along to the next nodes
    def forward(self, inputs: np.array):
        activation = inputs
        activations = np.array([inputs])
        zs = []
        for layer in self.layers:
            activation, z = layer.forward(activation)
            activations = np.append(activations, activation)
            zs = np.append(zs, z)
        return activation

    def details(self):
        for layer in self.layers:
            layer.definition()


# stores values to be processed by layers, uses dictionary and sorts by node UUID
class Values:
    def __init__(self, inputs=None, nodes=None):
        assert(len(inputs) == len(nodes))
        self.val = {}
        if inputs and nodes:
            for i in range(len(inputs)):
                self.insert(inputs[i], nodes[i].uuid)

    def __getitem__(self, item):
        return self.val[item]

    def __iter__(self):
        if hasattr(self.val[0], "__iter__"):
            return self.val[0].__iter__()
        return self.val.__iter__()

    def __len__(self):
        return len(self.val)

    def insert(self, input, node):
        if node in self.val:
            self.val[node].extend([input])
        else:
            self.val[node] = [input]

    def copy(self, values):
        self.val = values.val




