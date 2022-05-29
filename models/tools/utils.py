# ------------------------------------------------------------------------------
# Copyright (c) Microsoft
# Licensed under the MIT License.
# Written by Bin Xiao (Bin.Xiao@microsoft.com)
# ------------------------------------------------------------------------------

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import logging
import time
from pathlib import Path

import torch
import torch.optim as optim
import shutil
from models.core.config import get_model_name


def create_logger(cfg, cfg_path, flag="", phase='train'):
    time_str = time.strftime('%Y-%m-%d-%H-%M')
    root_output_dir = Path(cfg.OUTPUT_DIR)
    # set up logger
    if not root_output_dir.exists():
        print('=> creating {}'.format(root_output_dir))
        os.makedirs(root_output_dir)

    dataset = cfg.DATASET.DATASET + '_' + cfg.DATASET.HYBRID_JOINTS_TYPE if cfg.DATASET.HYBRID_JOINTS_TYPE else cfg.DATASET.DATASET
    dataset = dataset.replace(':', '_')
    _, full_name = get_model_name(cfg)
    # full_name = [full_name, cfg.TRAIN.LR, cfg.TRAIN.OPTIMIZER, cfg.MODEL.EXTRA.TARGET_TYPE, flag, time_str]
    try:
        full_name = [full_name, cfg.MODEL.EXTRA.NUM_DECONV_FILTERS[0], cfg.MODEL.EXTRA.TARGET_TYPE,
                     cfg.DATASET.ROT_FACTOR, flag, time_str]
    except:
        full_name = [full_name, cfg.MODEL.EXTRA.TARGET_TYPE, cfg.DATASET.ROT_FACTOR, flag, time_str]
    full_name = [str(f) for f in full_name if f]
    full_name = "_".join(full_name)
    final_output_dir = root_output_dir / dataset / full_name
    print('=> creating {}'.format(final_output_dir))
    final_output_dir.mkdir(parents=True, exist_ok=True)

    cfg_name = os.path.basename(cfg_path)
    shutil.copyfile(cfg_path, os.path.join(final_output_dir, cfg_name))
    log_file = '{}_{}_{}.log'.format("log", phase, time_str)
    final_log_file = final_output_dir / log_file
    head = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename=str(final_log_file), format=head)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    logging.getLogger('').addHandler(console)
    # tensorboard_log_dir = Path(cfg.LOG_DIR) / dataset / model / (cfg_name + '_' + time_str)
    tensorboard_log_dir = final_output_dir / "log"
    print('=> creating {}'.format(tensorboard_log_dir))
    tensorboard_log_dir.mkdir(parents=True, exist_ok=True)

    return logger, str(final_output_dir), str(tensorboard_log_dir)


def get_optimizer(cfg, model):
    optimizer = None
    if cfg.TRAIN.OPTIMIZER == 'sgd':
        optimizer = optim.SGD(
            model.parameters(),
            lr=cfg.TRAIN.LR,
            momentum=cfg.TRAIN.MOMENTUM,
            weight_decay=cfg.TRAIN.WD,
            nesterov=cfg.TRAIN.NESTEROV
        )
    elif cfg.TRAIN.OPTIMIZER == 'adam':
        optimizer = optim.Adam(
            model.parameters(),
            lr=cfg.TRAIN.LR
        )

    return optimizer


def save_checkpoint(states, is_best, output_dir, filename='checkpoint.pth.tar'):
    torch.save(states, os.path.join(output_dir, filename))
    if is_best and 'state_dict' in states:
        torch.save(states['state_dict'], os.path.join(output_dir, 'model_best.pth.tar'))
