---
title: "A Collection of PyTorch Trivia"
date: 2025-08-03
draft: false
language: en
description: "DES"
abstract: "Not that obscure, just a bit counterintuitive (to me)."
categories: ["Tech"]
tags: ["Machine Learning", "Code", "Tools"]
---

> This page was translated from the [original Chinese version](/zh-cn/posts/torch-hints) by Gemini. Please refer to the original for definitive content.

## Motivation
Recently at work, I came across a piece of `torch` trivia that none of my colleagues knew. It reminded me of a time when another `torch` quirk troubled me for a long time. So, I decided to write a summary of these functions that can easily lead to bugs if you just follow your intuition.

## How to Repeat in `torch`
As vector computation tools, the behavior of [`torch.repeat`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.repeat.html) is vastly different from [`numpy.repeat`](https://numpy.org/devdocs/reference/generated/numpy.repeat.html). The former duplicates the entire tensor along a given dimension, while the latter repeats each element along that dimension:
```bash
>>> torch.tensor([1, 2]).repeat(2)
tensor([1, 2, 1, 2])
>>> np.repeat(np.array([1, 2]), 2)
array([1, 1, 2, 2])
```

Counterintuitively, the function that behaves like `torch.repeat` is [`numpy.tile`](https://numpy.org/devdocs/reference/generated/numpy.tile.html), and the one that behaves like `numpy.repeat` is [`torch.repeat_interleave`](https://docs.pytorch.org/docs/stable/generated/torch.repeat_interleave.html). Interestingly, while writing this post, I noticed that the official PyTorch documentation for the `repeat` function now explicitly states that its behavior differs from `numpy.repeat`.

## A Tensor's View Cannot Be Modified In-Place

First, let's clarify what a "view" is. Creating a view of a tensor means presenting the tensor in a certain form (shape) while sharing the same underlying memory space with the original tensor. It doesn't create a new tensor in the physical sense. The `torch.Tensor.view` function always returns a view of a tensor. In contrast, `torch.Tensor.reshape` returns a view when possible, but if it can't (for example, if the original tensor's memory is not contiguous), it will create a copy of the original tensor.

For a tensor that requires gradients, if we create a view of it:

```python
a = torch.tensor([1, 2, 3, 4], dtype=float, requires_grad=True)
b = a.view(2, 2)
```

Then we cannot modify this view in-place:

```python
b[:, 0] += 5 # Error
b[:, 0] = 5 # Error
c = b[:, 0] + 5 # OK
```

This is because a view shares memory with the original Tensor. Modifying a view in-place directly changes the physical data, which affects the original Tensor and any other views pointing to the same memory. For Tensors that require gradient computation, this in-place operation breaks the integrity of the computation graph. Autograd cannot track this "indirect" data modification, which could lead to incorrect gradient calculations. Therefore, PyTorch prohibits this action. The correct approach is to `clone()` the corresponding tensor and then perform operations on the copy.