"""
信度分析模块
SRTP项目 - 计算Cronbach's alpha等信度指标
"""

import pandas as pd
import numpy as np


def cronbach_alpha(df):
    """
    计算Cronbach's alpha系数
    
    Formula: α = (k / k-1) * (1 - Σσ²i / σ²X)
    
    Parameters:
    -----------
    df : pd.DataFrame
        量表数据（列为题目，行為受试者）
        
    Returns:
    --------
    float
        Cronbach's alpha
    """
    n_items = df.shape[1]
    if n_items < 2:
        print("警告: 题目数量少于2，无法计算alpha")
        return np.nan
    
    # 计算每题的方差
    item_variances = df.var(axis=0, ddof=1)
    
    # 计算总分的方差
    total_scores = df.sum(axis=1)
    total_variance = total_scores.var(ddof=1)
    
    # 计算alpha
    alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
    
    return alpha


def cronbach_alpha_if_deleted(df):
    """
    计算删除某题后的alpha值（用于题目筛选）
    
    Parameters:
    -----------
    df : pd.DataFrame
        量表数据
        
    Returns:
    --------
    pd.DataFrame
        每个题目对应的alpha值
    """
    results = []
    n_items = df.shape[1]
    original_alpha = cronbach_alpha(df)
    
    for col in df.columns:
        df_without_item = df.drop(columns=[col])
        alpha_if_deleted = cronbach_alpha(df_without_item)
        results.append({
            'item': col,
            'alpha_if_deleted': alpha_if_deleted,
            'improvement': alpha_if_deleted - original_alpha
        })
    
    return pd.DataFrame(results)


def split_half_reliability(df):
    """
    折半信度
    
    Parameters:
    -----------
    df : pd.DataFrame
        量表数据
        
    Returns:
    --------
    dict
        折半信度结果
    """
    n_items = df.shape[1]
    if n_items % 2 == 0:
        # 偶数题目，直接对半分
        half1 = df.iloc[:, :n_items//2]
        half2 = df.iloc[:, n_items//2:]
    else:
        # 奇数题目，前半部分多一个
        half1 = df.iloc[:, :n_items//2 + 1]
        half2 = df.iloc[:, n_items//2 + 1:]
    
    # 计算两半的分数
    scores1 = half1.sum(axis=1)
    scores2 = half2.sum(axis=1)
    
    # 计算两半的相关系数
    r = scores1.corr(scores2)
    
    # Spearman-Brown校正
    n1, n2 = half1.shape[1], half2.shape[1]
    sb_corrected = (2 * r) / (1 + r)
    
    return {
        'correlation': r,
        'spearman_brown': sb_corrected,
        'guttman_split_half': 2 * (1 - np.sqrt(1 - r**2))
    }


def item_statistics(df):
    """
    题目统计量
    
    Parameters:
    -----------
    df : pd.DataFrame
        量表数据
        
    Returns:
    --------
    pd.DataFrame
        每题的统计量
    """
    results = []
    
    for col in df.columns:
        results.append({
            'item': col,
            'mean': df[col].mean(),
            'std': df[col].std(),
            'variance': df[col].var(),
            'skewness': df[col].skew(),
            'kurtosis': df[col].kurtosis(),
            'corrected_item_total_corr': corrected_item_total_correlation(df, col)
        })
    
    return pd.DataFrame(results)


def corrected_item_total_correlation(df, item_col):
    """
    计算校正的项总相关（CITC）
    
    Parameters:
    -----------
    df : pd.DataFrame
        量表数据
    item_col : str
        题目列名
        
    Returns:
    --------
    float
        CITC值
    """
    other_cols = [c for c in df.columns if c != item_col]
    item_scores = df[item_col]
    other_scores = df[other_cols].sum(axis=1)
    
    return item_scores.corr(other_scores)


def reliability_report(df, dimension_mapping):
    """
    生成完整的信度分析报告
    
    Parameters:
    -----------
    df : pd.DataFrame
        问卷数据
    dimension_mapping : dict
        维度到题目的映射
        
    Returns:
    --------
    dict
        信度分析报告
    """
    report = {}
    
    for dimension, cols in dimension_mapping.items():
        valid_cols = [c for c in cols if c in df.columns]
        if len(valid_cols) >= 2:
            dim_data = df[valid_cols]
            
            report[dimension] = {
                'n_items': len(valid_cols),
                'cronbach_alpha': cronbach_alpha(dim_data),
                'split_half': split_half_reliability(dim_data),
                'item_stats': item_statistics(dim_data)
            }
    
    return report


def interpret_alpha(alpha):
    """
    解释Cronbach's alpha值
    
    Parameters:
    -----------
    alpha : float
        alpha系数
        
    Returns:
    --------
    str
        解释说明
    """
    if alpha >= 0.9:
        return "优秀 (Excellent)"
    elif alpha >= 0.8:
        return "良好 (Good)"
    elif alpha >= 0.7:
        return "可接受 (Acceptable)"
    elif alpha >= 0.6:
        return "可疑 (Questionable)"
    elif alpha >= 0.5:
        return "差 (Poor)"
    else:
        return "不可接受 (Unacceptable)"


if __name__ == '__main__':
    print("信度分析模块测试...")
