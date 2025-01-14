
import os
from typing import Any
from tqdm import tqdm
import torch 
from datetime import datetime, timedelta
import config

# 将从torchvision中下载的数据集(非图片格式)转为图片格式
def transform_to_image(data, save_path: str):
    """
        data: 非图片数据
        save_path: 本地保存的路径
    """
    # 如果已经存在,不需要再转
    if os.path.exists(save_path):
        return
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # transform
    for i in tqdm(range(len(data))):
        img, label = data[i]
        img.save(os.path.join(save_path, str(i) + '-label-' + str(label) + '.png'))


# 数据转换类
class Compose(object):
    def __init__(self, transforms: list) -> None:
        """
        transforms: 一个列表, 存放各种转换形式, 例如Resize, ToTensor
        """
        self.transforms = transforms
    
    def __call__(self, imgs) -> Any:
        """
        imgs: PIL格式的图片数据
        """
        for t in self.transforms:
            imgs = t(imgs)
        return imgs
    
# Save the checkpoints
def save_checkpoints(checkpoints, log_dir, epoch):
    """
    Params:
        checkpoints: 模型权重
        log_dir: 日志目录
        epoch: 当前训练的轮数
    """
    # 若文件夹不存在，则创建
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    path = log_dir + f'/model_{epoch}.tar'
    print('==> Saving checkpoints')
    torch.save(checkpoints, path)


# 生成记录日志的文件夹
def build_log_folder():
    cur_time = datetime.now() + timedelta(hours=0)  # hours参数是时区
    log_path_dir = os.path.join(config.LOAD_MDEOL_FILE, cur_time.strftime(f"[%m-%d]%H.%M.%S"))
    # 若文件夹不存在，则创建
    if not os.path.exists(log_path_dir):
        os.makedirs(log_path_dir)
    return log_path_dir
    
