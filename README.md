# SwanLab-Train-WebUI

一个实验性项目，思考是可以基于训练启动脚本中的`swanlab.config`中的配置，来生成WebUI界面，来控制超参数以启动训练。

**Pipeline：**
1. 指定目标`config.yaml`文件与`train.py`文件
2. 获得`config.yaml`内容, 生成WebUI界面
3. 注入`config.yaml`中的参数，启动训练`python train.py`
4. 与swanlab的特性深度结合