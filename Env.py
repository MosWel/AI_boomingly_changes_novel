# Env.py

# 导入所需库
from pathlib import Path
import numpy as np

# 环境参数
DATA_PATH=Path('./兽血沸腾.epub') # 电子书路径
LT_VOLUME_IDX = [np.int64(0), np.int64(1), np.int64(11), np.int64(24), np.int64(35), np.int64(48), np.int64(65), np.int64(81), np.int64(91), -1] # 卷名所在序号
