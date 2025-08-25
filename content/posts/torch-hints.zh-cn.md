---
title: "PyTorch冷知识集锦"
date: 2025-08-03
draft: false
language: zh-cn
description: "DES"
abstract: "也没有很冷，只是有点反（我的）直觉。"
categories: ["技术"]
tags: ["机器学习", "开发", "工具"]
---

## Motivation
最近工作时遇到一个身边同事都不太知晓的`torch`冷知识，想起在之前某一段工作中也因为一些`torch`小知识困扰很久，故决定将这些仅凭直觉很容易写出bug的函数在此做一个小结。

## `torch`如何repeat
同样作为向量计算工具，[`torch.repeat`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.repeat.html)的行为和[`numpy.repeat`](https://numpy.org/devdocs/reference/generated/numpy.repeat.html)大相径庭。前者是在对应维度上复制整个向量，而后者是在对应维度上逐元素地重复：
```bash
>>>torch.tensor([1, 2]).repeat(2)
tensor([1, 2, 1, 2])
>>>np.repeat(np.array([1, 2]), 2)
array([1, 1, 2, 2])
```
反直觉地，与`torch.repeat`行为类似的是[`numpy.tile`](https://numpy.org/devdocs/reference/generated/numpy.tile.html)，而与`numpy.repeat`行为类似的是[`torch.repeat_interleave`](https://docs.pytorch.org/docs/stable/generated/torch.repeat_interleave.html)。有趣的是，我在写这篇文章的时候发现`PyTorch`的官方文档已经在`repeat`函数中注明了其与`numpy.repeat`行为不同。

## 一个tensor的view无法被原地更新
首先可能要明确什么是view。构造一个tensor的view是指提供这个tensor以某种形式（形状）的呈现，其与原tensor共享内存空间，并没有真正地、物理意义上的创建一个tensor。函数`torch.Tensor.view`返回的一定是某个tensor的view，而函数`torch.Tensor.reshape`则在能返回view时返回view，不能返回（例如，当原Tensor内存不连续时）时，则会创建一个原Tensor的副本。

在有梯度的tensor中，如果我们创建了某个tensor的view：
```python
a = torch.tensor([1, 2, 3, 4], dtype=float, require_grad=True)
b = a.view(2, 2)
```
则我们无法对这个view做inplace的更改：
```python
b[:, 0] += 5 # Error
b[:, 0] = 5 # Error
c = b[:, 0] + 5 # OK
```
这是因为view与原Tensor共享内存。对view进行原地修改，会直接改变物理数据，这会影响到原Tensor和其他所有指向这块内存的view。对于需要计算梯度的Tensor，这种原地操作会破坏计算图的完整性，autograd无法追踪到这种“间接”的数据修改，从而可能导致梯度计算错误，因此 PyTorch 禁止了这种行为。正确的做法是把相应的tensor给clone出来，再对副本进行操作。