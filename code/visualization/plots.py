"""
可视化模块
SRTP项目 - 多模态AI解读放射学报告对患者健康信念的影响研究

功能：
- 相关性热力图
- 维度得分分布图
- 散点图矩阵
- 回归诊断图
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def correlation_heatmap(corr_matrix, p_matrix=None, output_path=None, figsize=(10, 8)):
    """
    绘制相关性热力图
    
    Parameters:
    -----------
    corr_matrix : pd.DataFrame
        相关系数矩阵
    p_matrix : pd.DataFrame, optional
        p值矩阵（用于标记显著性）
    output_path : str
        输出路径
    figsize : tuple
        图形大小
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # 简化标签
    labels = [col.replace('_mean', '') for col in corr_matrix.columns]
    
    # 绘制热力图
    mask = np.zeros_like(corr_matrix)
    sns.heatmap(corr_matrix, 
                mask=mask,
                annot=True, 
                fmt='.2f',
                cmap='RdBu_r',
                center=0,
                vmin=-1, vmax=1,
                square=True,
                linewidths=0.5,
                xticklabels=labels,
                yticklabels=labels,
                ax=ax)
    
    ax.set_title('HBM维度相关矩阵', fontsize=14, pad=20)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ 相关性热力图已保存: {output_path}")
    
    plt.close()
    return fig


def dimension_boxplot(df, dimensions, output_path=None, figsize=(12, 6)):
    """
    绘制维度得分箱线图
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据（包含维度得分）
    dimensions : list
        维度列表
    output_path : str
        输出路径
    figsize : tuple
        图形大小
    """
    # 提取维度得分
    cols = [f'{dim}_mean' for dim in dimensions if f'{dim}_mean' in df.columns]
    data = df[cols].melt(var_name='dimension', value_name='score')
    data['dimension'] = data['dimension'].str.replace('_mean', '')
    
    fig, ax = plt.subplots(figsize=figsize)
    
    sns.boxplot(data=data, x='dimension', y='score', ax=ax, palette='Set2')
    sns.stripplot(data=data, x='dimension', y='score', ax=ax, 
                  color='black', alpha=0.3, size=3)
    
    ax.set_xlabel('HBM维度', fontsize=12)
    ax.set_ylabel('平均得分', fontsize=12)
    ax.set_title('各HBM维度得分分布', fontsize=14)
    ax.set_ylim(1, 5.5)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ 箱线图已保存: {output_path}")
    
    plt.close()
    return fig


def scatter_with_regression(df, x_dim, y_dim, output_path=None, figsize=(8, 6)):
    """
    绘制带回归线的散点图
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    x_dim : str
        X轴维度名
    y_dim : str
        Y轴维度名
    output_path : str
        输出路径
    figsize : tuple
        图形大小
    """
    x_col = f'{x_dim}_mean'
    y_col = f'{y_dim}_mean'
    
    df_plot = df[[x_col, y_col]].dropna()
    
    if len(df_plot) < 10:
        print(f"⚠️ 数据点不足")
        return None
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # 散点图
    ax.scatter(df_plot[x_col], df_plot[y_col], alpha=0.5, edgecolors='black', linewidth=0.5)
    
    # 回归线
    z = np.polyfit(df_plot[x_col], df_plot[y_col], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df_plot[x_col].min(), df_plot[x_col].max(), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=2, label='回归线')
    
    # 计算相关系数
    from scipy.stats import pearsonr
    r, pval = pearsonr(df_plot[x_col], df_plot[y_col])
    
    ax.set_xlabel(x_dim, fontsize=12)
    ax.set_ylabel(y_dim, fontsize=12)
    ax.set_title(f'{x_dim} vs {y_dim}\nr={r:.3f}, p={pval:.4f}', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ 散点图已保存: {output_path}")
    
    plt.close()
    return fig


def reliability_plot(df, dimensions, output_path=None, figsize=(10, 6)):
    """
    绘制信度系数条形图
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dimensions : list
        维度列表
    output_path : str
        输出路径
    figsize : tuple
        图形大小
    """
    from analysis.reliability import cronbach_alpha
    
    alphas = []
    dim_names = []
    
    for dim in dimensions:
        cols = []
        for prefix in ['H', 'S', 'B', 'R', 'C', 'E', 'T']:
            if dim.startswith('感知'):
                # 映射维度到题号前缀
                mapping = {
                    '感知易感性': 'H',
                    '感知严重性': 'S',
                    '感知益处': 'B',
                    '感知障碍': 'R',
                    '行动线索': 'C',
                    '自我效能': 'E'
                }
                prefix = mapping.get(dim, dim[0])
            
            # 查找对应的题目列
            for col in df.columns:
                if col.startswith(prefix):
                    cols.append(col)
        
        if cols:
            alpha, _ = cronbach_alpha(df[cols])
            alphas.append(alpha)
            dim_names.append(dim)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = ['green' if a >= 0.7 else 'orange' if a >= 0.6 else 'red' for a in alphas]
    
    bars = ax.barh(dim_names, alphas, color=colors, edgecolor='black')
    
    # 添加参考线
    ax.axvline(x=0.7, color='green', linestyle='--', alpha=0.7, label='可接受(0.7)')
    ax.axvline(x=0.8, color='blue', linestyle='--', alpha=0.7, label='良好(0.8)')
    
    ax.set_xlabel("Cronbach's α", fontsize=12)
    ax.set_title('各维度信度系数', fontsize=14)
    ax.set_xlim(0, 1)
    ax.legend()
    
    # 添加数值标签
    for bar, alpha in zip(bars, alphas):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, 
                f'{alpha:.3f}', va='center', fontsize=10)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ 信度图已保存: {output_path}")
    
    plt.close()
    return fig


def histogram_with_density(df, dimension, output_path=None, figsize=(8, 6)):
    """
    绘制带密度曲线的直方图
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dimension : str
        维度名
    output_path : str
        输出路径
    figsize : tuple
        图形大小
    """
    col = f'{dimension}_mean'
    
    if col not in df.columns:
        print(f"⚠️ 列 {col} 不存在")
        return None
    
    data = df[col].dropna()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # 直方图 + 密度曲线
    sns.histplot(data, kde=True, ax=ax, bins=10, color='steelblue', alpha=0.6)
    
    # 添加均值线
    mean_val = data.mean()
    ax.axvline(x=mean_val, color='red', linestyle='--', linewidth=2, label=f'M={mean_val:.2f}')
    
    ax.set_xlabel('得分', fontsize=12)
    ax.set_ylabel('频数', fontsize=12)
    ax.set_title(f'{dimension}得分分布', fontsize=14)
    ax.legend()
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ 直方图已保存: {output_path}")
    
    plt.close()
    return fig


def generate_all_plots(df, dimensions, output_dir='output'):
    """
    生成所有可视化图表
    
    Parameters:
    -----------
    df : pd.DataFrame
        数据
    dimensions : list
        维度列表
    output_dir : str
        输出目录
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    print("📊 生成可视化图表...")
    
    # 1. 相关性热力图
    from analysis.correlation import correlation_matrix
    corr, p_mat = correlation_matrix(df, dimensions)
    if corr is not None:
        correlation_heatmap(corr, p_mat, f'{output_dir}/correlation_heatmap.png')
    
    # 2. 维度得分箱线图
    dimension_boxplot(df, dimensions, f'{output_dir}/dimension_boxplot.png')
    
    # 3. 信度图
    reliability_plot(df, dimensions, f'{output_dir}/reliability_plot.png')
    
    # 4. 分布直方图
    for dim in dimensions[:3]:  # 只画前3个
        histogram_with_density(df, dim, f'{output_dir}/{dim}_histogram.png')
    
    print(f"✅ 所有图表已保存到 {output_dir}/")


if __name__ == '__main__':
    print("可视化模块测试...")
    print("请提供实际数据文件进行测试")
