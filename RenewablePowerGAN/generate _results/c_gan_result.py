"""
plot the results of generated data by C-GAN model

* @author: xuan
* @email: 1920425406@qq.com
* @date: 2023-12-22
"""

import sys
sys.path.append('C:\LemonLover\WorkSpace\DL\GANS\RenewablePowerGAN')

import torch
import random
import importlib
import os
from datetime import datetime, timedelta
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import config
from datasets.c_gan_dataset import SeasonDataset


def label_to_idx(class_: str):
    """
    Convert label to index

    Params:
        class_: the category to be generated
    """
    label_to_idx_dict = {
        'spring': 0,
        'summer': 1,
        "autumn": 2,
        'winter': 3
    }

    return label_to_idx_dict[class_]


def lineArg():
    """
    define the plot format
    """
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan', 'black', 'indianred', 'brown', 'firebrick', 'maroon', 'darkred', 'red', 'sienna', 'chocolate', 'yellow', 'olivedrab', 'yellowgreen', 'darkolivegreen', 'forestgreen', 'limegreen', 'darkgreen', 'green', 'lime', 'seagreen', 'mediumseagreen', 'darkslategray', 'darkslategrey', 'teal', 'darkcyan', 'dodgerblue', 'navy', 'darkblue', 'mediumblue', 'blue', 'slateblue', 'darkslateblue', 'mediumslateblue', 'mediumpurple', 'rebeccapurple', 'blueviolet', 'indigo', 'darkorchid', 'darkviolet', 'mediumorchid', 'purple', 'darkmagenta', 'fuchsia', 'magenta', 'orchid', 'mediumvioletred', 'deeppink', 'hotpink']
    markers = [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "X", "D", "d", "|", "_", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    linestyle = ['--', '-.', '-']
    line_arg = {}
    line_arg['color'] = random.choice(colors)
    # line_arg['marker'] = random.choice(markers)
    line_arg['linestyle'] = random.choice(linestyle)
    # line_arg['linewidth'] = random.randint(1, 4)
    return line_arg

def build_folder(arg_dict):
    """build the folder to save the results"""

    cur_time = datetime.now() + timedelta(hours=0)  # hours参数是时区
    # join the path
    result_dir = os.path.join(arg_dict["root_dir"], arg_dict["model"])
    result_dir = os.path.join(result_dir, cur_time.strftime(f"[%m-%d]%H.%M.%S"))

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    return result_dir

def plot(real_data, fake_data, arg_dict):
    """
    plot the data
    
    :param real_data: the data need to be ploted
    :param fake_data: the data need to be ploted
    """
    # set the random seed
    random.seed(0)
    
    assert len(real_data.shape) == 2, 'the real data to be ploted need multiple'
    assert len(fake_data.shape) == 2, 'the fake data to be ploted need multiple'

    ## pl0t the data
    plt.figure(figsize=(15, 5))

    # plot the real data
    plt.subplot(1, 2, 1)
    x = range(real_data.shape[1])
    for id in range(real_data.shape[0]):
        plt.plot(x, real_data[id], **lineArg())
    plt.title('real')
    plt.xlabel('time')
    plt.ylabel('power')

    # plot the fake data
    plt.subplot(1, 2, 2)
    x = range(fake_data.shape[1])
    for id in range(fake_data.shape[0]):
        plt.plot(x, fake_data[id], **lineArg())
    plt.title('fake')
    plt.xlabel('time')
    plt.ylabel('power')
    
    # show the plot or not
    if arg_dict["show"]:
        plt.show()

    # save the result or not
    if arg_dict["savefig"]:
        # build the folder
        result_dir = build_folder(arg_dict)
        plt.savefig(f'{result_dir}/result.png')


def main(arg_dict): 

    # load the trained model 
    impoted_model = importlib.import_module("model." + arg_dict["model"])
    generator = impoted_model.Generator(input_dim=config.Z_DIM, output_dim=config.OUTPUT_DIM)
    checkpoints = torch.load(arg_dict["checkpoints_path"])
    generator.load_state_dict(checkpoints["generator"])

    # load the real data
    solardataset = SeasonDataset(arg_dict["data"], normed=arg_dict["norm"])
    dataloader = DataLoader(
        dataset=solardataset,
        batch_size=365,
        shuffle=True
    )

    # label to index
    index = label_to_idx(arg_dict["class"])

    # real data
    for x, y in dataloader:
        indices = y==index
        real_data = x[indices]

    ## fake data
    # Randomly generte the noise and labels
    generator.eval()
    z = torch.randn(size=(len(real_data), config.Z_DIM))
    labels = torch.IntTensor([index] * len(real_data))
    fake_data = generator(z, labels).detach().cpu().numpy()
    
    # for normalize, if normed, the data should be midified
    if arg_dict["norm"] == 'norm':
        fake_data = fake_data * (solardataset.max - solardataset.min) + solardataset.min
        real_data = real_data * (solardataset.max - solardataset.min) + solardataset.min
    elif arg_dict["norm"] == 'standard':
        fake_data = fake_data * solardataset.std + solardataset.mean
        real_data = real_data * solardataset.std + solardataset.mean

    plot(real_data, fake_data, arg_dict)
    

if __name__ == '__main__':

    arg_dict = {
        "data": './data/changchun.xlsx',
        "model": 'c_gan_mlp',  # mlp, mlp_wgan, mlp_wgan_bt, c_gan_mlp
        "checkpoints_path": './logs/CGAN/[12-19]21.46.25/model_9999.tar',
        "savefig": False,
        "root_dir": './results/cgan',
        "norm": 'standard',  # norm or standard
        "class": 'autumn',
        "root_dir": './results/cgan',
        "show": True,
        "root_dir": './results/cgan',   # if "save" is True, the results will be saved to this dir
    }

    main(arg_dict)