"""
回归分析模块
SRTP项目 - 多模态AI解读放射学报告对患者健康信念的影响研究

功能：
- 多元线性回归
- 层次回归分析
- 回归诊断（多重共线性、异方差等）
- 效应量计算
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import warnings
warnings.filterwarnings('ignore')


def linear_regression(df, dependent_var, independent_vars, method='OLS'):
    """
    多元线性回归分析
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dependent_var : str
        因变量（维度名称，如'AI接受度'）
    independent_vars : list
        自变量列表（维度名称列表）
    method : str
        回归方法 ('OLS', 'WLS', 'GLM')
        
    Returns:
    --------
    statsmodels回归结果对象
    """
    # 构建变量名
    y_col = f'{dependent_var}_mean'
    X_cols = [f'{var}_mean' for var in independent_vars if f'{var}_mean' in df.columns]
    
    # 提取有效数据
    df_model = df[[y_col] + X_cols].dropna()
    
    if len(df_model) < len(X_cols) + 30:
        print(f"⚠️ 样本量不足 ({len(df_model)} < {len(X_cols) + 30})")
        return None
    
    y = df_model[y_col]
    X = df_model[X_cols]
    X = sm.add_constant(X)  # 添加常数项
    
    # 拟合模型
    if method == 'OLS':
        model = sm.OLS(y, X).fit()
    elif method == 'WLS':
        model = sm.WLS(y, X).fit()
    else:
        model = sm.GLM(y, X).fit()
    
    print(f"✅ 多元回归分析完成 (n={len(df_model)}, R²={model.rsquared:.3f})")
    return model


def hierarchical_regression(df, dependent_var, predictor_sets, covariables=None):
    """
    层次回归分析
    
    用于检验各预测变量集合对因变量的独立贡献
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dependent_var : str
        因变量
    predictor_sets : list of lists
        预测变量集合列表
        如: [['感知易感性', '感知严重性'], ['感知益处', '感知障碍'], ['自我效能']]
    covariables : list, optional
        控制变量
        
    Returns:
    --------
    list
        各层回归结果
    """
    results = []
    
    # 收集所有预测变量
    all_predictors = []
    for predictors in predictor_sets:
        all_predictors.extend(predictors)
    
    # 添加控制变量
    if covariables:
        all_predictors.extend(covariables)
    
    # 构建模型
    y_col = f'{dependent_var}_mean'
    df_model = df[[y_col]].copy()
    
    for predictors in predictor_sets:
        X_cols = []
        for var in predictors:
            col = f'{var}_mean'
            if col in df.columns:
                X_cols.append(col)
        
        # 添加已存在的变量
        for var in all_predictors:
            col = f'{var}_mean'
            if col in df.columns and col not in X_cols:
                X_cols.append(col)
        
        if len(X_cols) < 2:
            continue
            
        df_subset = df_model.join(df[X_cols]).dropna()
        
        if len(df_subset) < len(X_cols) + 30:
            continue
        
        y = df_subset[y_col]
        X = df_subset[X_cols]
        X = sm.add_constant(X)
        
        model = sm.OLS(y, X).fit()
        
        results.append({
            'n_predictors': len(X_cols) - 1,
            'n_samples': len(df_subset),
            'r_squared': model.rsquared,
            'adj_r_squared': model.rsquared_adj,
            'f_value': model.fvalue,
            'f_pvalue': model.f_pvalue,
            'model': model
        })
    
    # 打印层次回归结果
    print(f"\n📊 层次回归分析结果:")
    print("-" * 50)
    for i, res in enumerate(results):
        print(f"模型 {i+1}: R²={res['r_squared']:.3f}, 调整R²={res['adj_r_squared']:.3f}")
        print(f"         F={res['f_value']:.2f}, p={res['f_pvalue']:.4f}")
    
    return results


def vif_check(df, independent_vars):
    """
    检验多重共线性（VIF）
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    independent_vars : list
        自变量列表
        
    Returns:
    --------
    pd.DataFrame
        VIF结果表
    """
    X_cols = [f'{var}_mean' for var in independent_vars if f'{var}_mean' in df.columns]
    df_valid = df[X_cols].dropna()
    
    if len(df_valid) < len(X_cols) + 10:
        return None
    
    # 计算VIF
    X = df_valid.values
    vif_data = []
    
    for i, col in enumerate(X_cols):
        vif = variance_inflation_factor(X, i)
        vif_data.append({
            '变量': independent_vars[i],
            'VIF': round(vif, 2),
            '判断': '⚠️ 多重共线性' if vif > 10 else '✓ 可接受' if vif > 5 else '✓ 无问题'
        })
    
    return pd.DataFrame(vif_data)


def regression_diagnostics(df, dependent_var, independent_vars):
    """
    回归诊断
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dependent_var : str
        因变量
    independent_vars : list
        自变量列表
        
    Returns:
    --------
    dict
        诊断结果
    """
    y_col = f'{dependent_var}_mean'
    X_cols = [f'{var}_mean' for var in independent_vars if f'{var}_mean' in df.columns]
    
    df_valid = df[[y_col] + X_cols].dropna()
    
    if len(df_valid) < len(X_cols) + 30:
        return None
    
    y = df_valid[y_col]
    X = df_valid[X_cols]
    X = sm.add_constant(X)
    
    model = sm.OLS(y, X).fit()
    
    # 残差
    residuals = model.resid
    standardized = model.get_influence().resid_studentized_internal
    
    # 诊断检查
    diagnostics = {
        '样本量': len(df_valid),
        '自变量数': len(X_cols),
        'R²': round(model.rsquared, 4),
        '调整R²': round(model.rsquared_adj, 4),
        'F统计量': round(model.fvalue, 2),
        'F检验p值': round(model.f_pvalue, 6),
        
        # 正态性检验 (Shapiro-Wilk)
        '残差正态性p值': round(stats.shapiro(residuals)[1], 4) if len(residuals) < 5000 else 'N/A',
        
        # 异方差检验
        'BP检验p值': round(sm.stats.het_breuschpagan(residuals, X)[1], 4),
    }
    
    # 异常值检查
    outliers = np.where(np.abs(standardized) > 2)
    diagnostics['异常值个数'] = len(outliers[0])
    
    return diagnostics


def path_analysis(df, dependent_var, mediators, independent_vars):
    """
    路径分析（简化版中介效应检验）
    
    使用逐步法检验中介效应
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dependent_var : str
        因变量
    mediators : list
        中介变量列表
    independent_vars : list
        自变量列表
        
    Returns:
    --------
    dict
        路径分析结果
    """
    results = {}
    
    y_col = f'{dependent_var}_mean'
    
    # c路径: 自变量 -> 因变量
    for iv in independent_vars:
        iv_col = f'{iv}_mean'
        
        if iv_col not in df.columns or y_col not in df.columns:
            continue
        
        df_temp = df[[iv_col, y_col]].dropna()
        
        if len(df_temp) < 30:
            continue
        
        X = sm.add_constant(df_temp[[iv_col]])
        model_c = sm.OLS(df_temp[y_col], X).fit()
        
        results[f'{iv}_to_{dependent_var}'] = {
            'c': model_c.params.get(iv_col, 0),
            'p_c': model_c.pvalues.get(iv_col, 1),
            'R²_c': model_c.rsquared
        }
        
        # a路径: 自变量 -> 中介变量
        for med in mediators:
            med_col = f'{med}_mean'
            
            if med_col not in df.columns:
                continue
            
            df_med = df[[iv_col, med_col]].dropna()
            
            if len(df_med) < 30:
                continue
            
            X_a = sm.add_constant(df_med[[iv_col]])
            model_a = sm.OLS(df_med[med_col], X_a).fit()
            
            key_a = f'{iv}_to_{med}'
            if key_a not in results:
                results[key_a] = {}
            results[key_a]['a'] = model_a.params.get(iv_col, 0)
            results[key_a]['p_a'] = model_a.pvalues.get(iv_col, 1)
            
            # b路径: 中介变量 -> 因变量（控制自变量）
            df_ab = df[[iv_col, med_col, y_col]].dropna()
            
            if len(df_ab) < 30:
                continue
            
            X_ab = sm.add_constant(df_ab[[iv_col, med_col]])
            model_b = sm.OLS(df_ab[y_col], X_ab).fit()
            
            key_ab = f'{iv}_to_{dependent_var}_via_{med}'
            results[key_ab]['b'] = model_b.params.get(med_col, 0)
            results[key_ab]['p_b'] = model_b.pvalues.get(med_col, 1)
            results[key_ab]['c_prime'] = model_b.params.get(iv_col, 0)
            results[key_ab]['p_c_prime'] = model_b.pvalues.get(iv_col, 1)
            
            # 中介效应估计 (a*b)
            results[key_ab]['ab'] = results[key_a]['a'] * results[key_ab]['b']
    
    return results


def regression_report(df, dependent_var, independent_vars):
    """
    生成回归分析报告
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dependent_var : str
        因变量
    independent_vars : list
        自变量列表
        
    Returns:
    --------
    str
        报告文本
    """
    # 1. 多元回归
    model = linear_regression(df, dependent_var, independent_vars)
    
    if model is None:
        return "⚠️ 样本量不足，无法进行回归分析"
    
    # 2. VIF检验
    vif_df = vif_check(df, independent_vars)
    
    # 3. 回归诊断
    diag = regression_diagnostics(df, dependent_var, independent_vars)
    
    # 4. 构建报告
    report = f"""
{'='*60}
多元回归分析报告
{'='*60}

1. 模型摘要
   样本量: {diag['样本量']}
   自变量数: {diag['自变量数']}
   R²: {diag['R²']:.4f}
   调整R²: {diag['调整R²']:.4f}
   F({diag['自变量数']}, {diag['样本量']-diag['自变量数']-1}) = {diag['F统计量']:.2f}, p = {diag['F检验p值']:.6f}

2. 回归系数
{model.summary().tables[1].as_text()}

3. 多重共线性检验 (VIF)
"""
    
    if vif_df is not None:
        report += vif_df.to_string(index=False)
    else:
        report += "   样本量不足"
    
    report += f"""

4. 回归诊断
   残差正态性p值: {diag['残差正态性p值']} {'(>0.05为正态)' if isinstance(diag['残差正态性p值'], float) else ''}
   异方差检验p值: {diag['BP检验p值']:.4f} {'(>0.05为同方差)' if diag['BP检验p值'] else ''}
   异常值个数: {diag['异常值个数']}

5. 效应量参照标准
   R² = 0.02: 小效应
   R² = 0.13: 中效应
   R² = 0.26: 大效应
"""
    
    return report


if __name__ == '__main__':
    print("回归分析模块测试...")
    print("请提供实际数据文件进行测试")
