# SRTP项目代码 - 数据分析模块

## 项目概述
基于健康信念模型(HBM)分析多模态AI解读放射学报告对患者的影响

## 数据结构（问卷）
- 人口统计学: 5题
- HBM维度: 32题 (6个维度)
- AI接受度: 5题
- 总计: ~37题 (Likert 5点量表)

## 目录结构

```
code/
├── data_preprocessing/  # 数据预处理
│   └── data_loader.py
├── analysis/          # 统计分析
│   ├── descriptive.py     # 描述性统计
│   ├── reliability.py     # 信度分析(Cronbach α)
│   ├── validity.py       # 效度分析
│   └── correlation.py     # 相关性分析
├── models/            # 建模
│   ├── regression.py     # 回归分析
│   ├── sem.py          # 结构方程模型
│   └── factor_analysis.py # 因子分析
└── visualization/    # 可视化
    └── plots.py
```

## 使用方法

```python
# 1. 加载数据
from data_preprocessing.data_loader import load_survey_data
df = load_survey_data('path/to/your/data.csv')

# 2. 描述性统计
from analysis.descriptive import descriptive_stats
stats = descriptive_stats(df)

# 3. 信度分析
from analysis.reliability import cronbach_alpha
alpha = cronbach_alpha(df, dimension_cols)

# 4. 回归分析
from models.regression import hbm_regression
results = hbm_regression(df)
```

## 分析方法清单

### 描述性统计
- 均值、标准差、中位数
- 分布检验(正态性)
- 频数分析

### 信度分析
- Cronbach's α系数
- 折半信度

### 效度分析
- KMO检验
- Bartlett球形检验
- 探索性因子分析(EFA)

### 相关性分析
- Pearson相关系数
- Spearman等级相关

### 建模分析
- 多元线性回归
- Logistic回归(如果因变量是二分类)
- 结构方程模型(SEM)
- 中介效应分析

## 依赖包
- pandas
- numpy
- scipy
- statsmodels
- scikit-learn
- matplotlib
- seaborn
- pingouin (推荐，用于SEM)
