"""
数据加载模块
SRTP项目 - 多模态AI解读放射学报告对患者健康信念的影响研究
"""

import pandas as pd
import numpy as np
from pathlib import Path

# 问卷题目标识（基于 questionnaire_design.md）
DIMENSION_MAPPING = {
    # 人口统计学
    'demographics': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
    
    # HBM维度
    '感知易感性': ['H1', 'H2', 'H3', 'H4'],
    '感知严重性': ['S1', 'S2', 'S3', 'S4'],
    '感知益处': ['B1', 'B2', 'B3', 'B4', 'B5'],
    '感知障碍': ['R1', 'R2', 'R3', 'R4', 'R5', 'R6'],
    '行动线索': ['C1', 'C2', 'C3', 'C4'],
    '自我效能': ['E1', 'E2', 'E3', 'E4'],
    
    # AI接受度
    'AI接受度': ['T1', 'T2', 'T3', 'T4', 'T5']
}


def load_survey_data(file_path, encoding='utf-8'):
    """
    加载问卷数据
    
    Parameters:
    -----------
    file_path : str
        数据文件路径 (CSV或Excel)
    encoding : str
        文件编码
        
    Returns:
    --------
    pd.DataFrame
        问卷数据
    """
    path = Path(file_path)
    
    if path.suffix == '.csv':
        df = pd.read_csv(file_path, encoding=encoding)
    elif path.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {path.suffix}")
    
    print(f"✅ 数据加载成功: {df.shape[0]} 行, {df.shape[1]} 列")
    return df


def clean_data(df, missing_threshold=0.3):
    """
    数据清洗
    
    Parameters:
    -----------
    df : pd.DataFrame
        原始数据
    missing_threshold : float
        缺失比例阈值，超过则删除该列
        
    Returns:
    --------
    pd.DataFrame
        清洗后的数据
    """
    # 删除缺失值过多的列
    missing_ratio = df.isnull().sum() / len(df)
    cols_to_keep = missing_ratio[missing_ratio < missing_threshold].index
    df_clean = df[cols_to_keep].copy()
    
    # 删除完全重复的行
    df_clean = df_clean.drop_duplicates()
    
    # 处理异常值 (Likert量表应该是1-5)
    likert_cols = [col for col in df_clean.columns if any(dim in col for dim in ['H', 'S', 'B', 'R', 'C', 'E', 'T'])]
    for col in likert_cols:
        df_clean = df_clean[(df_clean[col] >= 1) & (df_clean[col] <= 5)]
    
    print(f"✅ 数据清洗完成: {df_clean.shape[0]} 行, {df_clean.shape[1]} 列")
    return df_clean


def calculate_dimension_scores(df):
    """
    计算各维度得分
    
    Parameters:
    -----------
    df : pd.DataFrame
        清洗后的数据
        
    Returns:
    --------
    pd.DataFrame
        包含维度得分的DataFrame
    """
    df_scores = df.copy()
    
    for dimension, cols in DIMENSION_MAPPING.items():
        valid_cols = [c for c in cols if c in df.columns]
        if valid_cols:
            # 计算维度平均分
            df_scores[f'{dimension}_mean'] = df[valid_cols].mean(axis=1)
            # 计算维度总分
            df_scores[f'{dimension}_sum'] = df[valid_cols].sum(axis=1)
    
    print(f"✅ 维度得分计算完成")
    return df_scores


def get_column_mapping(df_columns):
    """
    自动识别列对应的维度
    
    Parameters:
    -----------
    df_columns : list
        DataFrame的列名
        
    Returns:
    --------
    dict
        列名到维度的映射
    """
    mapping = {}
    for col in df_columns:
        for dim, cols in DIMENSION_MAPPING.items():
            if col in cols:
                mapping[col] = dim
                break
    return mapping


if __name__ == '__main__':
    # 测试代码
    print("数据加载模块测试...")
    print("请提供实际数据文件路径进行测试")
