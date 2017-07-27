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
+ 最大最小搜索和 Alpha-Beta 剪枝：剪枝的效率很可能有问题；
+ 增加迭代加深，但是用时间限制迭代加深的实现有问题，有可能会走出明显的漏勺；
+ 支持设置是否带禁手；

### 二、近期目标

+ 针对已经致胜的情况，增加路线图，避免反复计算
+ 已经必败的点，在迭代加深时为什么还要考虑？

| 方法                     |     次数 |    耗时 |
| ---------------------- | -----: | ----: |
| base_linear            | 257733 |  2.05 |
| inside_line_grouping   | 176497 | 0.538 |
| inside_make_line       |   4553 | 3.556 |
| judge                  |   4595 | 0.294 |
| judge_first            |   4595 | 0.221 |
| judge_second           |      7 | 0.003 |
| win_chance_single_line |    816 | 0.008 |
| win_chance_mul_lines   |    688 | 0.029 |
| normal_chance          |    295 | 0.002 |
| gen                    |    816 | 0.676 |
| evaluate               |   3730 | 2.967 |
| move                   |   4595 | 0.318 |
| min_max_search         |      4 |  3.99 |
| iterative_deepening    |      1 | 3.991 |

### 三、待添加

+ 解题时输出路径（目前只输出了第一步）
+ 置换表：
+ 后台思考：至少得把UI改成异步的。