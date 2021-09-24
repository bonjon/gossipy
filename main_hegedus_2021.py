from gossipy.model.sampling import TorchModelPartition
import torch
from torch.nn.modules.loss import CrossEntropyLoss
from networkx import to_numpy_matrix
from networkx.generators.random_graphs import random_regular_graph
from gossipy import set_seed, AntiEntropyProtocol, CreateModelMode
from gossipy.node import GossipNode, PartitioningBasedNode, SamplingBasedNode
from gossipy.model.handler import PartitionedTMH, SamplingTMH, TorchModelHandler
from gossipy.model.nn import LogisticRegression
from gossipy.data import load_classification_dataset, DataDispatcher
from gossipy.data.handler import ClassificationDataHandler
from gossipy.simul import GossipSimulator, plot_evaluation


set_seed(98765)
X, y = load_classification_dataset("spambase", as_tensor=True)
data_handler = ClassificationDataHandler(X, y, test_size=.1)
dispatcher = DataDispatcher(data_handler, n=100, eval_on_user=False)
topology = to_numpy_matrix(random_regular_graph(20, 100, seed=42))

# sim = GossipSimulator(
#     data_dispatcher=dispatcher,
#     delta=100,
#     protocol=AntiEntropyProtocol.PUSH, 
#     gossip_node_class=GossipNode,
#     model_handler_class=TorchModelHandler,
#     model_handler_params={
#         "net" : LogisticRegression(data_handler.Xtr.shape[1], 2), #TorchMLP
#         "optimizer" : torch.optim.SGD,
#         "l2_reg": .001,
#         "criterion" : CrossEntropyLoss(),
#         "learning_rate" : .1,
#         "create_model_mode" : CreateModelMode.MERGE_UPDATE
#     },
#     topology=topology,
#     delay=(0, 10),
#     sampling_eval=.1,
#     round_synced=True
# )
# sim.init_nodes()
# evaluation, evaluation_user = sim.start(n_rounds=1000)

net = LogisticRegression(data_handler.Xtr.shape[1], 2)
sim = GossipSimulator(
    data_dispatcher=dispatcher,
    delta=100,
    protocol=AntiEntropyProtocol.PUSH, 
    gossip_node_class=SamplingBasedNode,
    model_handler_class=SamplingTMH,
    #gossip_node_class=PartitioningBasedNode,
    #model_handler_class=PartitionedTMH,
    model_handler_params={
        "sample_size" : .5,
        #"tm_partition": TorchModelPartition(net, 5),
        "net" : net,
        "optimizer" : torch.optim.SGD,
        "l2_reg": .001,
        "criterion" : CrossEntropyLoss(),
        "learning_rate" : 1,
        "create_model_mode" : CreateModelMode.UPDATE
    },
    topology=topology,
    delay=(0, 1),
    sampling_eval=.1,
    round_synced=True
)
sim.init_nodes()
evaluation, evaluation_user = sim.start(n_rounds=100)

print(sim.nodes[0].model_handler.model.model.weight.detach().numpy())

plot_evaluation([evaluation])
plot_evaluation([evaluation_user])