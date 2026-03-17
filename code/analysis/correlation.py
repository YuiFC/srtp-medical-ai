"""
相关性分析模块
SRTP项目 - 多模态AI解读放射学报告对患者健康信念的影响研究

功能：
- Pearson相关分析
- Spearman等级相关
- 相关矩阵可视化
- 偏相关分析
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


def correlation_matrix(df, dimensions, method='pearson', min_samples=10):
    """
    计算维度间的相关矩阵
    
    Parameters:
    -----------
    df : pd.DataFrame
        包含维度得分的DataFrame
    dimensions : list
        维度列表
    method : str
        相关方法 ('pearson', 'spearman', 'kendall')
    min_samples : int
        最少样本数
        
    Returns:
    --------
    pd.DataFrame
        相关系数矩阵
    pd.DataFrame
        p值矩阵
    """
    # 提取维度平均分列
    dim_cols = [f'{dim}_mean' for dim in dimensions if f'{dim}_mean' in df.columns]
    
    if not dim_cols:
        # 尝试直接使用原始题目
        dim_cols = dimensions
    
    # 过滤有效数据
    df_valid = df[dim_cols].dropna()
    
    if len(df_valid) < min_samples:
        print(f"⚠️ 有效样本不足 ({len(df_valid)} < {min_samples})")
        return None, None
    
    # 计算相关矩阵
    corr_matrix = df_valid.corr(method=method)
    
    # 计算p值矩阵
    n_dims = len(dim_cols)
    p_matrix = pd.DataFrame(np.zeros((n_dims, n_dims)), 
                           index=dim_cols, columns=dim_cols)
    
    for i, col1 in enumerate(dim_cols):
        for j, col2 in enumerate(dim_cols):
            if i != j:
                if method == 'pearson':
                    _, p = stats.pearsonr(df_valid[col1], df_valid[col2])
                else:
                    _, p = stats.spearmanr(df_valid[col1], df_valid[col2])
                p_matrix.iloc[i, j] = p
            else:
                p_matrix.iloc[i, j] = 0
    
    print(f"✅ 相关矩阵计算完成 (n={len(df_valid)}, method={method})")
    return corr_matrix, p_matrix


def dimension_correlations(df, target_dim, predictor_dims, method='pearson'):
    """
    计算目标维度与预测维度间的相关性
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    target_dim : str
        目标维度（如'AI接受度'）
    predictor_dims : list
        预测维度列表
    method : str
        相关方法
        
    Returns:
    --------
    pd.DataFrame
        相关分析结果表
    """
    results = []
    
    target_col = f'{target_dim}_mean'
    
    for pred_dim in predictor_dims:
        pred_col = f'{pred_dim}_mean'
        
        # 获取有效数据对
        valid_data = df[[target_col, pred_col]].dropna()
        
        if len(valid_data) < 10:
            continue
        
        if method == 'pearson':
            r, p = stats.pearsonr(valid_data[target_col], valid_data[pred_col])
        else:
            r, p = stats.spearmanr(valid_data[target_col], valid_data[pred_col])
        
        # 相关强度解释
        abs_r = abs(r)
        if abs_r < 0.1:
            strength = '无相关'
        elif abs_r < 0.3:
            strength = '弱相关'
        elif abs_r < 0.5:
            strength = '中等相关'
        elif abs_r < 0.7:
            strength = '较强相关'
        else:
            strength = '强相关'
        
        # 方向
        direction = '正' if r > 0 else '负'
        
        results.append({
            '预测变量': pred_dim,
            '相关系数(r)': round(r, 4),
            'p值': round(p, 4),
            '相关强度': strength,
            '相关方向': direction,
            '样本量': len(valid_data),
            '显著性': '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        })
    
    return pd.DataFrame(results)


def partial_correlation(df, var1, var2, control_vars):
    """
    偏相关分析
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    var1 : str
        变量1（列名）
    var2 : str
        变量2（列名）
    control_vars : list
        控制变量列表
        
    Returns:
    --------
    tuple
        (偏相关系数, p值)
    """
    from scipy.stats import pearsonr
    
    # 提取需要的列
    cols = [var1, var2] + control_vars
    df_valid = df[cols].dropna()
    
    if len(df_valid) < len(control_vars) + 10:
        return None, None
    
    # 计算偏相关
    # 使用公式: r12.3 = (r12 - r13*r23) / sqrt((1-r13^2)*(1-r23^2))
    
    r12 = pearsonr(df_valid[var1], df_valid[var2])[0]
    
    partial_r = r12
    for covar in control_vars:
        r13 = pearsonr(df_valid[var1], df_valid[covar])[0]
        r23 = pearsonr(df_valid[var2], df_valid[covar])[0]
        
        denominator = np.sqrt((1 - r13**2) * (1 - r23**2))
        if denominator > 0:
            partial_r = (partial_r - r13 * r23) / denominator
    
    # 计算t统计量和p值
    n = len(df_valid)
    k = len(control_vars)
    df = n - k - 2
    
    if df > 0:
        t = partial_r * np.sqrt(df / (1 - partial_r**2))
        p = 2 * (1 - stats.t.cdf(abs(t), df))
    else:
        p = None
    
    return partial_r, p


def correlation_report(df, dimensions, target_dim='AI接受度'):
    """
    生成完整相关分析报告
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dimensions : list
        维度列表
    target_dim : str
        目标维度
        
    Returns:
    --------
    str
        报告文本
    """
    # 预测维度（排除目标维度）
    predictor_dims = [d for d in dimensions if d != target_dim]
    
    # 1. 维度间相关矩阵
    corr_matrix, p_matrix = correlation_matrix(df, dimensions, method='pearson')
    
    # 2. 各维度与目标变量的相关
    dim_corr = dimension_correlations(df, target_dim, predictor_dims)
    
    report = f"""
{'='*60}
相关性分析报告
{'='*60}

1. 目标变量: {target_dim}

2. 各维度与{target_dim}的相关分析:
{dim_corr.to_string(index=False)}

3. 相关强度参照标准:
   |r| < 0.1: 无相关
   0.1 ≤ |r| < 0.3: 弱相关
   0.3 ≤ |r| < 0.5: 中等相关
   0.5 ≤ |r| < 0.7: 较强相关
   |r| ≥ 0.7: 强相关

4. 显著性水平:
   * p < 0.05
   ** p < 0.01
   *** p < 0.001
"""
    
    return report, corr_matrix, dim_corr


if __name__ == '__main__':
    print("相关性分析模块测试...")
    print("请提供实际数据文件进行测试")
