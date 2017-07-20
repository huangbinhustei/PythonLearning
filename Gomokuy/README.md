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
+ “伪”最大最小搜索：和最大最小无关，仅仅是在决策出胜负时跳出搜索。
+ 增加迭代加深，并区别对待：
  - 解题时按照深度
  - 对弈时按照时间

### 二、待添加

+ 最大最小搜索和 Alpha-Beta 剪枝；
+ 解题时输出路径（目前只输出了第一步）
+ 置换表
+ 后台思考