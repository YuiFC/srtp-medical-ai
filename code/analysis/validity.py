"""
效度分析模块
- 探索性因子分析(EFA)
- 验证性因子分析(CFA)
- 效度指标计算
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings

try:
    from factor_analyzer import FactorAnalyzer
    from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
    FACTOR_ANALYZER_AVAILABLE = True
except ImportError:
    FACTOR_ANALYZER_AVAILABLE = False
    warnings.warn("factor_analyzer未安装，因子分析功能将受限")

try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
except ImportError:
    pass


class ValidityAnalyzer:
    """效度分析类"""
    
    def __init__(self, data: pd.DataFrame):
        """
        初始化效度分析器
        
        Parameters:
        -----------
        data : pd.DataFrame
            问卷数据
        """
        self.data = data
        self.results = {}
    
    def content_validity(self, expert_ratings: np.ndarray) -> dict:
        """
        内容效度：专家评分法
        
        Parameters:
        -----------
        expert_ratings : np.ndarray
            专家评分矩阵 (n_items, n_experts)
            每个专家对每个题目的相关性评分(1-4)
        
        Returns:
        --------
        dict : 内容效度指标
        """
        # 计算内容效度指数(CVI)
        # 3或4分视为"相关"
        relevant = (expert_ratings >= 3).sum(axis=1)  # 每个题目被判定为相关的专家数
        cvi_item = relevant / expert_ratings.shape[1]  # 题目水平CVI
        
        # 全体一致CVI (Universal agreement)
        cvi_universal = cvi_item.mean()
        
        # 随机一致性概率
        n_categories = len(np.unique(expert_ratings))
        pc = (1 / n_categories)  # 随机一致概率
        
        # 修正一致性CVI (ACVI)
        cvi_acvi = (cvi_universal - pc) / (1 - pc) if pc < 1 else cvi_universal
        
        self.results['content_validity'] = {
            'cvi_item': cvi_item.tolist(),
            'cvi_universal': cvi_universal,
            'cvi_acvi': cvi_acvi,
            'interpretation': 'CVI > 0.80 为可接受' if cvi_universal >= 0.80 else 'CVI < 0.80，需修订题目'
        }
        
        return self.results['content_validity']
    
    def kmo_test(self) -> dict:
        """
        KMO检验 - 因子分析适用性
        
        Returns:
        --------
        dict : KMO检验结果
        """
        if not FACTOR_ANALYZER_AVAILABLE:
            # 手动计算KMO（近似）
            corr_matrix = self.data.corr()
            inv_corr = np.linalg.inv(corr_matrix)
            partial_corr = -inv_corr / np.sqrt(np.outer(np.diag(inv_corr), np.diag(inv_corr)))
            np.fill_diagonal(partial_corr, 0)
            
            sum_sq_corr = np.sum(corr_matrix.values ** 2) - len(corr_matrix)
            sum_sq_partial = np.sum(partial_corr ** 2)
            
            kmo = sum_sq_corr / (sum_sq_corr + sum_sq_partial)
            
            return {
                'kmo': kmo,
                'interpretation': self._interpret_kmo(kmo)
            }
        
        kmo_all, kmo_model = calculate_kmo(self.data)
        
        return {
            'kmo': kmo_model,
            'interpretation': self._interpret_kmo(kmo_model)
        }
    
    def _interpret_kmo(self, kmo: float) -> str:
        """解释KMO值"""
        if kmo >= 0.9:
            return "非常好 (meritorious)"
        elif kmo >= 0.8:
            return "良好 (middling)"
        elif kmo >= 0.7:
            return "一般 (mediocre)"
        elif kmo >= 0.6:
            return "较差 (poor)"
        elif kmo >= 0.5:
            return "很差 (poor)"
        else:
            return "不可接受 (unacceptable)"
    
    def bartlett_test(self) -> dict:
        """
        Bartlett球形检验
        
        Returns:
        --------
        dict : 检验结果
        """
        if not FACTOR_ANALYZER_AVAILABLE:
            # 使用简化版本
            corr_matrix = self.data.corr()
            n = len(self.data)
            chi_square = -(n - 1 - (2 * len(self.data.columns) + 5) / 6) * np.log(np.linalg.det(corr_matrix))
            df = len(self.data.columns) * (len(self.data.columns) - 1) / 2
            p_value = 1 - stats.chi2.cdf(chi_square, df)
            
            return {
                'chi_square': chi_square,
                'df': df,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        
        chi_square, p_value = calculate_bartlett_sphericity(self.data)
        
        return {
            'chi_square': chi_square,
            'df': int(p_value.df),
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    def exploratory_factor_analysis(self, n_factors: int = None, method: str = 'principal') -> dict:
        """
        探索性因子分析(EFA)
        
        Parameters:
        -----------
        n_factors : int, optional
            因子数量，默认为None（自动确定）
        method : str
            提取方法: 'principal' (主成分) 或 'ml' (最大似然)
        
        Returns:
        --------
        dict : EFA结果
        """
        if not FACTOR_ANALYZER_AVAILABLE:
            return {'error': '需要安装 factor_analyzer 库'}
        
        # 自动确定因子数（特征值>1）
        if n_factors is None:
            fa = FactorAnalyzer(rotation=None)
            fa.fit(self.data)
            eigenvalues = fa.get_eigenvalues()[0]
            n_factors = sum(eigenvalues > 1)
        
        # 执行因子分析
        if method == 'ml':
            fa = FactorAnalyzer(n_factors=n_factors, rotation='varimax', method='maximum likelihood')
        else:
            fa = FactorAnalyzer(n_factors=n_factors, rotation='varimax', method='principal')
        
        fa.fit(self.data)
        
        # 获取因子载荷
        loadings = pd.DataFrame(
            fa.loadings_,
            index=self.data.columns,
            columns=[f'Factor{i+1}' for i in range(n_factors)]
        )
        
        # 方差解释
        variance = fa.get_factor_variance()
        
        # 因子得分
        scores = pd.DataFrame(
            fa.transform(self.data),
            columns=[f'Factor{i+1}' for i in range(n_factors)]
        )
        
        # 共同度
        communalities = pd.Series(
            fa.get_communalities(),
            index=self.data.columns,
            name='Communalities'
        )
        
        result = {
            'n_factors': n_factors,
            'loadings': loadings.to_dict(),
            'variance_explained': {
                'ss_loadings': variance[0].tolist(),
                'proportion': variance[1].tolist(),
                'cumulative': variance[2].tolist()
            },
            'communalities': communalities.to_dict(),
            'factor_scores': scores.to_dict(),
            'interpretation': self._interpret_factor_analysis(loadings, communalities)
        }
        
        self.results['efa'] = result
        return result
    
    def _interpret_factor_analysis(self, loadings: pd.DataFrame, communalities: pd.Series) -> str:
        """解释因子分析结果"""
        # 检查载荷>0.4的题目比例
        high_loadings = (loadings.abs() > 0.4).sum().sum()
        total = loadings.shape[0] * loadings.shape[1]
        
        # 检查共同度
        low_communality = (communalities < 0.3).sum()
        
        return (
            f"载荷>0.4的比例: {high_loadings}/{total} ({100*high_loadings/total:.1f}%), "
            f"共同度<0.3的题目数: {low_communality}"
        )
    
    def confirmatory_factor_analysis(self, factor_structure: dict) -> dict:
        """
        验证性因子分析(CFA) - 简化版
        
        Parameters:
        -----------
        factor_structure : dict
            因子结构, e.g., {'Factor1': ['Q1', 'Q2', 'Q3'], 'Factor2': ['Q4', 'Q5']}
        
        Returns:
        --------
        dict : CFA结果（简化版，提供拟合指标估计）
        """
        # 简化版CFA - 计算聚合效度指标
        results = {}
        
        for factor_name, items in factor_structure.items():
            if all(item in self.data.columns for item in items):
                subset = self.data[items]
                
                # 计算组合信度(CR)
                n_items = len(items)
                Cronbach_alpha = self._cronbach_alpha(subset)
                cr = (n_items ** 2 * subset.corr().values.mean()) / (
                    1 + (n_items - 1) * subset.corr().values.mean()
                )
                
                # 计算平均方差抽取(AVE)
                loadings_sq = subset.corr().values ** 2
                np.fill_diagonal(loadings_sq, 0)
                ave = loadings_sq.sum() / (n_items * (n_items - 1))
                
                results[factor_name] = {
                    'n_items': n_items,
                    'cronbach_alpha': Cronbach_alpha,
                    'composite_reliability': cr,
                    'ave': ave,
                    'validity': '良好' if ave >= 0.5 else '需改进'
                }
        
        self.results['cfa'] = results
        return results
    
    def _cronbach_alpha(self, data: pd.DataFrame) -> float:
        """计算Cronbach's alpha"""
        n_items = data.shape[1]
        item_variances = data.var(axis=0, ddof=1)
        total_variance = data.sum(axis=1).var(ddof=1)
        
        alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
        return alpha
    
    def convergent_discriminant_validity(self, dimension_scores: pd.DataFrame) -> dict:
        """
        收敛效度与区分效度检验
        
        Parameters:
        -----------
        dimension_scores : pd.DataFrame
            各维度得分（列名为维度名）
        
        Returns:
        --------
        dict : 效度检验结果
        """
        # 收敛效度：AVE > 0.5
        ave_values = {}
        for col in dimension_scores.columns:
            var = dimension_scores[col].var(ddof=1)
            ave_values[col] = var  # 维度得分方差作为AVE近似
        
        # 区分效度：维度间相关系数 < AVE的平方根
        corr_matrix = dimension_scores.corr()
        np.fill_diagonal(corr_matrix.values, 0)
        
        discriminant_valid = True
        for i, col1 in enumerate(corr_matrix.columns):
            for j, col2 in enumerate(corr_matrix.columns):
                if i < j:
                    corr = abs(corr_matrix.loc[col1, col2])
                    if corr >= np.sqrt(ave_values[col1]) or corr >= np.sqrt(ave_values[col2]):
                        discriminant_valid = False
        
        result = {
            'ave': ave_values,
            'convergent_valid': all(v >= 0.5 for v in ave_values.values()),
            'discriminant_valid': discriminant_valid,
            'corr_matrix': corr_matrix.to_dict()
        }
        
        self.results['validity'] = result
        return result
    
    def generate_report(self) -> str:
        """生成效度分析报告"""
        report = ["=" * 60, "效度分析报告", "=" * 60, ""]
        
        # KMO检验
        if 'kmo' in self.results:
            kmo_result = self.results['kmo']
            report.append(f"KMO检验: {kmo_result['kmo']:.3f}")
            report.append(f"  → {kmo_result['interpretation']}")
            report.append("")
        
        # Bartlett检验
        if 'bartlett' in self.results:
            bt_result = self.results['bartlett']
            report.append(f"Bartlett球形检验:")
            report.append(f"  χ² = {bt_result['chi_square']:.2f}, df = {bt_result['df']}")
            report.append(f"  p-value = {bt_result['p_value']:.4f}")
            report.append(f"  {'✓ 显著，适合因子分析' if bt_result['significant'] else '✗ 不显著'}")
            report.append("")
        
        # 因子分析
        if 'efa' in self.results:
            efa = self.results['efa']
            report.append(f"探索性因子分析 (EFA):")
            report.append(f"  因子数量: {efa['n_factors']}")
            report.append(f"  累计方差解释: {100*efa['variance_explained']['cumulative'][-1]:.1f}%")
            report.append(f"  {efa['interpretation']}")
            report.append("")
        
        # 收敛/区分效度
        if 'validity' in self.results:
            val = self.results['validity']
            report.append("效度评估:")
            report.append(f"  收敛效度: {'✓ 良好' if val['convergent_valid'] else '✗ 需改进'}")
            report.append(f"  区分效度: {'✓ 良好' if val['discriminant_valid'] else '✗ 需改进'}")
        
        return "\n".join(report)


def run_validity_analysis(data: pd.DataFrame, dimension_scores: pd.DataFrame = None, 
                          factor_structure: dict = None) -> dict:
    """
    便捷函数：运行完整效度分析
    
    Parameters:
    -----------
    data : pd.DataFrame
        原始问卷数据
    dimension_scores : pd.DataFrame, optional
        维度得分数据
    factor_structure : dict, optional
        因子结构（用于CFA）
    
    Returns:
    --------
    dict : 分析结果
    """
    analyzer = ValidityAnalyzer(data)
    
    # KMO和Bartlett检验
    kmo_result = analyzer.kmo_test()
    bartlett_result = analyzer.bartlett_test()
    
    # EFA（可选）
    efa_result = None
    if data.shape[1] >= 10:  # 至少10个题目
        try:
            efa_result = analyzer.exploratory_factor_analysis()
        except Exception as e:
            efa_result = {'error': str(e)}
    
    # CFA（如果提供了因子结构）
    cfa_result = None
    if factor_structure:
        cfa_result = analyzer.confirmatory_factor_analysis(factor_structure)
    
    # 收敛/区分效度（如果提供了维度得分）
    validity_result = None
    if dimension_scores is not None:
        validity_result = analyzer.convergent_discriminant_validity(dimension_scores)
    
    return {
        'kmo': kmo_result,
        'bartlett': bartlett_result,
        'efa': efa_result,
        'cfa': cfa_result,
        'validity': validity_result,
        'report': analyzer.generate_report()
    }


if __name__ == "__main__":
    # 示例用法
    print("效度分析模块")
    print("使用方法:")
    print("  from analysis.validity import ValidityAnalyzer, run_validity_analysis")
    print("  result = run_validity_analysis(questionnaire_data, dimension_scores)")
