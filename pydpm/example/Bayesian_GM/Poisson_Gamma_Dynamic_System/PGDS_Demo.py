"""
===========================================
Poisson Gamma Dynamical Systems Demo
Aaron Schein, Hanna Wallach and Mingyuan Zhou
Published in Neural Information Processing Systems 2016

===========================================

"""

# Author: Chaojie Wang <xd_silly@163.com>; Jiawen Wu <wjw19960807@163.com>; Wei Zhao <13279389260@163.com>
# License: BSD-3-Clause

import numpy as np
import scipy.io as sio

from pydpm.metric import ACC
from pydpm.model import PGDS

from torchvision import datasets, transforms
from pydpm.dataloader.image_data import tensor_transforms

# load dataset
# define transform for dataset and load orginal dataset
transform = transforms.Compose([transforms.ToTensor()])
train_dataset = datasets.MNIST(root='../../dataset/mnist/', train=True, download=True)
test_dataset = datasets.MNIST(root='../../dataset/mnist/', train=False, download=False)

# transform dataset and reshape the dataset into [batch_size, feature_num]
train_data = tensor_transforms(train_dataset.data, transform)
train_data = train_data.permute(1, 0, 2).reshape(len(train_dataset), -1)# len(train_dataset, 28*28)
test_data = tensor_transforms(test_dataset.data, transform)
test_data = test_data.permute(1, 0, 2).reshape(len(test_dataset), -1)
train_label = train_dataset.train_labels
test_label = test_dataset.test_labels

# transpose the dataset to fit the model and convert a tensor to numpy array
train_data = np.array(np.ceil(train_data[:999, :].T.numpy() * 5), order='C')
test_data = np.array(np.ceil(test_data[:999, :].T.numpy() * 5), order='C')
train_label = train_label.numpy()[:999]
test_label = test_label.numpy()[:999]

# create the model and deploy it on gpu or cpu
model = PGDS(100, 'gpu')
model.initial(train_data)
train_local_params = model.train(200, train_data)
train_local_params = model.test(200, train_data)
test_local_params = model.test(200, test_data)

# evaluate the model with classification accuracy
# the demo accuracy can achieve 0.8739
results = ACC(train_local_params.Theta, test_local_params.Theta, train_label, test_label, 'SVM')

# save the model after training
model.save()
# model.load('./save_models/PGDS.npy')

