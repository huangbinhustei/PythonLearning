# 五子棋

 ![](https://img.shields.io/badge/Python-3.6-blue.svg) ![](https://img.shields.io/badge/Flask-0.12-blue.svg)

 ![](https://img.shields.io/badge/禁手-支持-brightgreen.svg) ![](https://img.shields.io/badge/三手两打-不支持-red.svg) ![](https://img.shields.io/badge/五手交换-不支持-red.svg)

## 使用方法

+ 对弈：python3 apps.py
+ 解题：题目录入 conf.py，然后 python3 gomokuy.py

## 记录

### 一、已实现

+ 简单的基于 Flask 的 UI；
+ 简单的局势评估函数，简单的启发式搜索；
+ 最大最小搜索和 Alpha-Beta 剪枝：剪枝的效率很可能有问题
+ 增加迭代加深，但是用时间限制迭代加深的实现有问题，有可能会走出明显的漏勺。

### 二、近期目标

+ 针对已经致胜的情况，增加路线图，避免反复计算
+ 已经必败的点，在迭代加深时为什么还要考虑？

### 三、待添加

+ 解题时输出路径（目前只输出了第一步）
+ 置换表
+ 后台思考