"""
SRTP项目 - 主分析脚本
多模态AI解读放射学报告对患者健康信念的影响研究

使用方法:
    python main_analysis.py --data path/to/data.csv
    
    # 只运行特定分析
    python main_analysis.py --data path/to/data.csv --analysis descriptive correlation
    python main_analysis.py --data path/to/data.csv --analysis regression
    python main_analysis.py --data path/to/data.csv --analysis all --visualize
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# 导入分析模块
sys.path.insert(0, str(Path(__file__).parent))

from data_preprocessing.data_loader import (
    load_survey_data, clean_data, calculate_dimension_scores, DIMENSION_MAPPING
)
from analysis.descriptive import descriptive_stats, dimension_stats
from analysis.reliability import cronbach_alpha, reliability_report, interpret_alpha
from analysis.correlation import correlation_matrix, dimension_correlations, correlation_report
from analysis.regression import linear_regression, vif_check, hierarchical_regression, regression_report
from analysis.validity import ValidityAnalyzer, run_validity_analysis


# 默认维度列表（用于分析）
HBM_DIMENSIONS = [
    '感知易感性', '感知严重性', '感知益处', 
    '感知障碍', '行动线索', '自我效能', 'AI接受度'
]


def run_descriptive_analysis(df, df_scores, dimensions, output_dir):
    """运行描述性统计分析"""
    print("\n" + "="*50)
    print("[1/6] 描述性统计分析")
    print("="*50)
    
    # 获取HBM维度映射
    dimension_mapping = {f'{k}_mean': v for k, v in DIMENSION_MAPPING.items() 
                   if k in [d.replace('_mean', '') for d in dimensions]}
    
    # 各维度统计
    dim_stats = dimension_stats(df_scores, dimension_mapping)
    print("\n各维度描述性统计:")
    print(dim_stats[['dimension', 'mean', 'std', 'median', 'alpha']].to_string(index=False))
    
    # 保存结果
    dim_stats.to_csv(f'{output_dir}/dimension_stats.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 描述性统计结果已保存: {output_dir}/dimension_stats.csv")
    
    return dim_stats


def run_reliability_analysis(df, dimensions, output_dir):
    """运行信度分析"""
    print("\n" + "="*50)
    print("[2/6] 信度分析")
    print("="*50)
    
    hbm_mapping = {k: v for k, v in DIMENSION_MAPPING.items() 
                   if k in dimensions}
    
    reliability_results = reliability_report(df, hbm_mapping)
    
    print("\n各维度Cronbach's α:")
    for dim, result in reliability_results.items():
        alpha = result['cronbach_alpha']
        interpretation = interpret_alpha(alpha)
        print(f"  {dim}: {alpha:.3f} ({interpretation})")
    
    # 保存详细报告
    with open(f'{output_dir}/reliability_report.txt', 'w', encoding='utf-8') as f:
        f.write("信度分析报告\n")
        f.write("="*50 + "\n\n")
        for dim, result in reliability_results.items():
            alpha = result['cronbach_alpha']
            f.write(f"{dim}:\n")
            f.write(f"  题目数: {result['n_items']}\n")
            f.write(f"  Cronbach's α: {alpha:.4f}\n")
            f.write(f"  解释: {interpret_alpha(alpha)}\n\n")
    
    print(f"✅ 信度分析报告已保存: {output_dir}/reliability_report.txt")
    
    return reliability_results


def run_correlation_analysis(df, dimensions, target_dim='AI接受度', output_dir=None):
    """运行相关性分析"""
    print("\n" + "="*50)
    print("[3/6] 相关性分析")
    print("="*50)
    
    # 1. 相关矩阵
    corr_matrix, p_matrix = correlation_matrix(df, dimensions, method='pearson')
    
    if corr_matrix is not None:
        # 保存相关矩阵
        corr_matrix.to_csv(f'{output_dir}/correlation_matrix.csv', encoding='utf-8-sig')
        print(f"✅ 相关矩阵已保存: {output_dir}/correlation_matrix.csv")
    
    # 2. 各维度与目标变量相关
    predictor_dims = [d for d in dimensions if d != target_dim]
    dim_corr = dimension_correlations(df, target_dim, predictor_dims)
    
    if not dim_corr.empty:
        print(f"\n各维度与{target_dim}的相关:")
        print(dim_corr.to_string(index=False))
        
        # 保存
        dim_corr.to_csv(f'{output_dir}/target_correlations.csv', index=False, encoding='utf-8-sig')
    
    # 3. 生成报告
    report, _, _ = correlation_report(df, dimensions, target_dim)
    print(report)
    
    with open(f'{output_dir}/correlation_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 相关性分析报告已保存: {output_dir}/correlation_report.txt")
    
    return corr_matrix, dim_corr


def run_regression_analysis(df, dependent_var, independent_vars, output_dir):
    """运行回归分析"""
    print("\n" + "="*50)
    print("[4/6] 回归分析")
    print("="*50)
    
    # 1. 多元回归
    model = linear_regression(df, dependent_var, independent_vars)
    
    if model is None:
        print("⚠️ 样本量不足，跳过回归分析")
        return None
    
    # 打印回归结果
    print(f"\n多元回归结果 (因变量: {dependent_var}):")
    print(model.summary())
    
    # 2. VIF检验
    vif_df = vif_check(df, independent_vars)
    if vif_df is not None:
        print(f"\n多重共线性检验 (VIF):")
        print(vif_df.to_string(index=False))
        vif_df.to_csv(f'{output_dir}/vif_results.csv', index=False, encoding='utf-8-sig')
    
    # 3. 保存回归结果
    with open(f'{output_dir}/regression_summary.txt', 'w', encoding='utf-8') as f:
        f.write(str(model.summary()))
    
    # 保存系数表
    coef_df = pd.DataFrame({
        '变量': model.params.index,
        '系数': model.params.values,
        '标准误': model.bse.values,
        't值': model.tvalues.values,
        'p值': model.pvalues.values,
        '95%CI下限': model.conf_int()[0].values,
        '95%CI上限': model.conf_int()[1].values
    })
    coef_df.to_csv(f'{output_dir}/regression_coefficients.csv', index=False, encoding='utf-8-sig')
    
    print(f"✅ 回归分析结果已保存: {output_dir}/")
    
    return model


def run_hierarchical_regression(df, dependent_var, predictor_sets, covariables=None, output_dir=None):
    """运行层次回归分析"""
    print("\n" + "="*50)
    print("[5/6] 层次回归分析")
    print("="*50)
    
    results = hierarchical_regression(df, dependent_var, predictor_sets, covariables)
    
    if not results:
        print("⚠️ 样本量不足，跳过层次回归分析")
        return None
    
    # 保存结果
    summary = []
    for i, res in enumerate(results):
        summary.append({
            '模型': f'模型{i+1}',
            '预测变量数': res['n_predictors'],
            '样本量': res['n_samples'],
            'R²': res['r_squared'],
            '调整R²': res['adj_r_squared'],
            'F值': res['f_value'],
            'p值': res['f_pvalue']
        })
    
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(f'{output_dir}/hierarchical_regression_summary.csv', 
                      index=False, encoding='utf-8-sig')
    
    print(f"✅ 层次回归结果已保存: {output_dir}/hierarchical_regression_summary.csv")
    
    return results


def run_visualization(df, dimensions, output_dir):
    """生成可视化图表"""
    print("\n" + "="*50)
    print("[6/6] 可视化图表生成")
    print("="*50)
    
    try:
        from visualization.plots import (
            correlation_heatmap, dimension_boxplot, 
            scatter_with_regression, reliability_plot
        )
        from analysis.correlation import correlation_matrix
        
        # 1. 相关性热力图
        corr, _ = correlation_matrix(df, dimensions)
        if corr is not None:
            correlation_heatmap(corr, output_path=f'{output_dir}/correlation_heatmap.png')
        
        # 2. 箱线图
        dimension_boxplot(df, dimensions, f'{output_dir}/dimension_boxplot.png')
        
        # 3. 信度图
        reliability_plot(df, dimensions, f'{output_dir}/reliability_plot.png')
        
        print(f"✅ 可视化图表已保存: {output_dir}/")
        
    except ImportError as e:
        print(f"⚠️ 可视化模块导入失败: {e}")
    except Exception as e:
        print(f"⚠️ 可视化生成失败: {e}")


def main(data_path, output_dir='output', analysis='all', visualize=False):
    """
    主分析流程
    
    Parameters:
    -----------
    data_path : str
        数据文件路径
    output_dir : str
        输出目录
    analysis : str
        分析类型: 'all', 'descriptive', 'reliability', 'correlation', 'regression'
    visualize : bool
        是否生成可视化
    """
    print("="*60)
    print("SRTP项目 - 数据分析")
    print("多模态AI解读放射学报告对患者健康信念的影响研究")
    print("="*60)
    
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    
    # 1. 加载数据
    print(f"\n[加载] 读取数据: {data_path}")
    df = load_survey_data(data_path)
    print(f"原始数据: {df.shape[0]} 行, {df.shape[1]} 列")
    
    # 2. 数据清洗
    print("\n[清洗] 数据清洗...")
    df_clean = clean_data(df)
    
    # 3. 计算维度得分
    print("\n[得分] 计算维度得分...")
    df_scores = calculate_dimension_scores(df_clean)
    
    # 确定分析维度 (使用中文名)
    dimensions = [d for d in HBM_DIMENSIONS if d in DIMENSION_MAPPING]
    
    # 运行分析
    if analysis in ['all', 'descriptive']:
        run_descriptive_analysis(df_clean, df_scores, dimensions, output_dir)
    
    if analysis in ['all', 'reliability']:
        run_reliability_analysis(df_clean, dimensions, output_dir)
    
    if analysis in ['all', 'correlation']:
        run_correlation_analysis(df_scores, dimensions, 'AI接受度', output_dir)
    
    if analysis in ['all', 'regression']:
        # 多元回归
        predictors = [d for d in dimensions if d != 'AI接受度']
        run_regression_analysis(df_scores, 'AI接受度', predictors, output_dir)
        
        # 层次回归示例
        predictor_sets = [
            ['感知易感性', '感知严重性'],
            ['感知益处', '感知障碍'],
            ['行动线索', '自我效能']
        ]
        run_hierarchical_regression(df_scores, 'AI接受度', predictor_sets, output_dir=output_dir)
    
    if visualize:
        run_visualization(df_scores, dimensions, output_dir)
    
    # 总结
    print("\n" + "="*60)
    print("✅ 分析完成！")
    print("="*60)
    print(f"\n生成的文件:")
    for f in Path(output_dir).iterdir():
        print(f"  - {f.name}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SRTP项目数据分析')
    parser.add_argument('--data', type=str, required=True, help='数据文件路径')
    parser.add_argument('--output', type=str, default='output', help='输出目录')
    parser.add_argument('--analysis', type=str, default='all',
                       choices=['all', 'descriptive', 'reliability', 'correlation', 'regression'],
                       help='分析类型')
    parser.add_argument('--visualize', action='store_true', help='生成可视化图表')
    parser.add_argument('--target', type=str, default='AI接受度', help='目标变量')
    
    args = parser.parse_args()
    
    main(args.data, args.output, args.analysis, args.visualize)
