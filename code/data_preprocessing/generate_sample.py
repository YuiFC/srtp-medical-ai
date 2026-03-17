"""
示例问卷数据
用于测试分析脚本

注意：这是模拟数据，仅供开发测试使用
"""

import pandas as pd
import numpy as np

def generate_sample_data(n=100, seed=42):
    """生成模拟问卷数据"""
    np.random.seed(seed)
    
    # 人口统计学信息
    data = {
        'Q1_age': np.random.randint(18, 70, n),  # 年龄
        'Q2_gender': np.random.choice([1, 2], n),  # 性别
        'Q3_edu': np.random.randint(1, 6, n),  # 学历
        'Q4_exp': np.random.choice([1, 2], n, p=[0.7, 0.3]),  # 检查经历
        'Q5_ai_know': np.random.randint(1, 6, n),  # AI了解程度
    }
    
    # HBM维度题项 (采用Likert 5点量表)
    # 感知易感性
    for i in range(1, 5):
        data[f'H{i}'] = np.random.randint(2, 6, n)
    
    # 感知严重性
    for i in range(1, 5):
        data[f'S{i}'] = np.random.randint(2, 6, n)
    
    # 感知益处
    for i in range(1, 6):
        data[f'B{i}'] = np.random.randint(3, 6, n)
    
    # 感知障碍 (反向，得分越高障碍越大)
    for i in range(1, 7):
        data[f'R{i}'] = np.random.randint(1, 5, n)
    
    # 行动线索
    for i in range(1, 5):
        data[f'C{i}'] = np.random.randint(2, 6, n)
    
    # 自我效能
    for i in range(1, 5):
        data[f'E{i}'] = np.random.randint(2, 6, n)
    
    # AI接受度
    for i in range(1, 6):
        data[f'T{i}'] = np.random.randint(2, 6, n)
    
    df = pd.DataFrame(data)
    return df


if __name__ == '__main__':
    df = generate_sample_data(100)
    print(f"生成数据: {df.shape}")
    print(df.head())
    # 保存为CSV
    df.to_csv('sample_data.csv', index=False, encoding='utf-8-sig')
    print("已保存到 sample_data.csv")
