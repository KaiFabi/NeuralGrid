"""File with helper functions."""
import math

import torch
import torchvision
from torch.utils.data import DataLoader
from torchvision import transforms as transforms


def xavier_init(size, fan_in, fan_out):
    """Custom Xavier initialization for neural grid."""
    limit = math.sqrt(6.0 / (fan_in + fan_out))
    x = torch.empty(size=size).uniform_(-limit, limit)
    return x


def comp_metrics(model, data_loader, device):
    """Function to compute metrics for test dataset.

    Due to slow inference speed, only n_test_samples randomly selected
    data samples are processed per pass.

    Args:
        model: An instance of a nn.Model class.
        data_loader: An instance of DataLoader
        device: String

    Returns: two floats, loss and accuracy

    """

    loss_func = torch.nn.CrossEntropyLoss()

    running_loss = 0.0
    running_accuracy = 0.0
    running_counter = 0

    with torch.no_grad():

        for i, data in enumerate(data_loader):
            inputs, labels = data[0].to(device), data[1].to(device)

            # Preparing input data
            x = inputs
            y = labels.long()

            # Feedforward
            y_pred = model(x)

            # Loss
            loss = loss_func(input=y_pred, target=y)

            # Metrics
            running_loss += loss.item()
            running_accuracy += (torch.argmax(y_pred, dim=-1) == y).float().sum()
            running_counter += labels.size(0)

    loss = running_loss / running_counter
    accuracy = running_accuracy / running_counter

    return loss, accuracy


def data_generator(cfg):
    """Return train and test loader of specified dataset.

    Args:
        cfg: dictionary holding configuration information

    Returns:

    """

    avg = (0.5,)
    std = (0.5,)

    transform_train = transforms.Compose([transforms.ToTensor(),
                                          transforms.Normalize(avg, std)])

    transform_test = transforms.Compose([transforms.ToTensor(),
                                         transforms.Normalize(avg, std)])

    if cfg["data"]["name"] == "mnist":
        train_set = torchvision.datasets.MNIST(root=cfg["paths"]["data"],
                                               train=True,
                                               download=True,
                                               transform=transform_train)

        test_set = torchvision.datasets.MNIST(root=cfg["paths"]["data"],
                                              train=False,
                                              download=True,
                                              transform=transform_test)
    elif cfg["data"]["name"] == "fashion_mnist":
        train_set = torchvision.datasets.FashionMNIST(root=cfg["paths"]["data"],
                                                      train=True,
                                                      download=True,
                                                      transform=transform_train)

        test_set = torchvision.datasets.FashionMNIST(root=cfg["paths"]["data"],
                                                     train=False,
                                                     download=True,
                                                     transform=transform_test)
    else:
        raise NotImplementedError("Dataset not available.")

    train_loader = DataLoader(train_set,
                              batch_size=cfg["training"]["batch_size"],
                              shuffle=True,
                              drop_last=True,
                              num_workers=cfg["training"]["n_workers"])

    test_loader = DataLoader(test_set,
                             batch_size=cfg["testing"]["batch_size"],
                             shuffle=True,
                             drop_last=True,
                             num_workers=cfg["training"]["n_workers"])

    return train_loader, test_loader
