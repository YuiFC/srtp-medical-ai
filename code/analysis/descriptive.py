"""
描述性统计分析模块
SRTP项目
"""

import pandas as pd
import numpy as np
from scipy import stats


def descriptive_stats(df, columns=None):
    """
    计算描述性统计量
    
    Parameters:
    -----------
    df : pd.DataFrame
        问卷数据
    columns : list, optional
        要分析的列，默认所有数值列
        
    Returns:
    --------
    pd.DataFrame
        描述性统计表
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    desc = df[columns].describe().T
    
    # 添加更多统计量
    desc['median'] = df[columns].median()
    desc['mode'] = df[columns].mode().iloc[0]
    desc['skewness'] = df[columns].skew()
    desc['kurtosis'] = df[columns].kurtosis()
    desc['range'] = desc['max'] - desc['min']
    desc['cv'] = desc['std'] / desc['mean'] * 100  # 变异系数
    
    return desc


def normality_test(df, columns=None, alpha=0.05):
    """
    正态性检验
    
    Parameters:
    -----------
    df : pd.DataFrame
        问卷数据
    columns : list, optional
        要检验的列
    alpha : float
        显著性水平
        
    Returns:
    --------
    pd.DataFrame
        检验结果表
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    results = []
    for col in columns:
        # Shapiro-Wilk检验 (样本量<5000时效果好)
        if len(df) <= 5000:
            stat, p = stats.shapiro(df[col].dropna())
        else:
            # Kolmogorov-Smirnov检验 (大样本)
            stat, p = stats.kstest(df[col].dropna(), 'norm')
        
        results.append({
            'column': col,
            'statistic': stat,
            'p_value': p,
            'is_normal': p > alpha
        })
    
    return pd.DataFrame(results)


def frequency_analysis(df, column):
    """
    频数分析
    
    Parameters:
    -----------
    df : pd.DataFrame
        问卷数据
    column : str
        列名
        
    Returns:
    --------
    pd.DataFrame
        频数分析表
    """
    freq = df[column].value_counts().sort_index()
    pct = freq / len(df) * 100
    
    result = pd.DataFrame({
        'value': freq.index,
        'count': freq.values,
        'percentage': pct.values
    })
    
    return result


def dimension_stats(df, dimension_mapping):
    """
    计算各维度的描述性统计
    
    Parameters:
    -----------
    df : pd.DataFrame
        问卷数据
    dimension_mapping : dict
        维度到列名的映射
        
    Returns:
    --------
    pd.DataFrame
        各维度统计表
    """
    results = []
    
    for dim, cols in dimension_mapping.items():
        valid_cols = [c for c in cols if c in df.columns]
        if valid_cols:
            dim_data = df[valid_cols]
            results.append({
                'dimension': dim,
                'n_items': len(valid_cols),
                'mean': dim_data.mean().mean(),
                'std': dim_data.stack().std(),
                'median': dim_data.median().median(),
                'min': dim_data.min().min(),
                'max': dim_data.max().max(),
                'alpha': cronbach_alpha_simple(dim_data)  # 简化的alpha计算
            })
    
    return pd.DataFrame(results)


def cronbach_alpha_simple(df):
    """
    简化的Cronbach's alpha计算
    
    Parameters:
    -----------
    df : pd.DataFrame
        维度数据（多列）
        
    Returns:
    --------
    float
        Cronbach's alpha
    """
    n_items = df.shape[1]
    if n_items < 2:
        return np.nan
    
    item_vars = df.var(axis=0, ddof=1)
    total_var = df.sum(axis=1).var(ddof=1)
    
    alpha = (n_items / (n_items - 1)) * (1 - item_vars.sum() / total_var)
    return alpha


if __name__ == '__main__':
    print("描述性统计分析模块测试...")
