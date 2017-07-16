# 五子棋

 ![](https://img.shields.io/badge/Python-3.6-blue.svg) 

 ![](https://img.shields.io/badge/禁手-支持-brightgreen.svg) ![](https://img.shields.io/badge/三手两打-不支持-red.svg) ![](https://img.shields.io/badge/五手交换-不支持-red.svg)

## 一、已有

+ 简单的基于 Flask 的游戏 UI；
+ 简单的局势评估函数；
+ “伪”最大最小搜索：和最大最小无关，仅仅是在决策出胜负时跳出搜索。

## 二、待添加

+ 最大最小搜索和 Alpha-Beta 剪枝；
+ 决策结果记录，避免反复计算；
+ 解题时输出路径（目前只输出了第一步）