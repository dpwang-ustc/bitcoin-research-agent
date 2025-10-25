"""
Bitcoin Research Agent - 市场状态识别模型

功能：
1. 识别市场状态：震荡(Consolidation)、趋势(Trending)、恐慌(Panic)、狂热(Euphoria)
2. 使用K-Means聚类和Hidden Markov Model
3. 生成Market Regime指标时间序列

作者：Bitcoin Research Agent Team
日期：2025-10-25
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from hmmlearn import hmm
import warnings
warnings.filterwarnings('ignore')


class MarketRegimeIdentifier:
    """市场状态识别器"""
    
    # 市场状态定义
    REGIMES = {
        0: 'Consolidation',  # 震荡：低波动率、窄幅震荡
        1: 'Trending',       # 趋势：明确方向、持续动能
        2: 'Panic',          # 恐慌：高波动、急剧下跌、恐惧
        3: 'Euphoria'        # 狂热：高波动、急剧上涨、贪婪
    }
    
    REGIME_CN = {
        0: '震荡',
        1: '趋势',
        2: '恐慌',
        3: '狂热'
    }
    
    def __init__(self, n_regimes: int = 4, method: str = 'kmeans', verbose: bool = True):
        """
        初始化市场状态识别器
        
        Args:
            n_regimes: 市场状态数量（默认4个）
            method: 识别方法 ('kmeans', 'hmm', 'hybrid')
            verbose: 是否打印详细信息
        """
        self.n_regimes = n_regimes
        self.method = method
        self.verbose = verbose
        
        # 模型
        self.kmeans_model = None
        self.hmm_model = None
        self.scaler = StandardScaler()
        self.pca = None
        
        # 状态映射
        self.regime_mapping = None
    
    def log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[MarketRegime] {message}")
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """
        准备用于状态识别的特征
        
        Args:
            df: 输入DataFrame (来自特征工程)
        
        Returns:
            特征数组, 特征名称列表
        """
        self.log("准备特征数据...")
        
        # 关键特征选择
        feature_columns = []
        
        # 1. 价格动量特征
        momentum_features = ['Return', 'Return_7d', 'Return_30d']
        for feat in momentum_features:
            col = f'market_{feat}' if f'market_{feat}' in df.columns else feat
            if col in df.columns:
                feature_columns.append(col)
        
        # 2. 波动率特征
        volatility_features = ['Volatility_7d', 'Volatility_30d']
        for feat in volatility_features:
            col = f'market_{feat}' if f'market_{feat}' in df.columns else feat
            if col in df.columns:
                feature_columns.append(col)
        
        # 3. 技术指标
        technical_features = ['RSI14', 'MACD', 'BB_Width', 'ATR14']
        for feat in technical_features:
            col = f'market_{feat}' if f'market_{feat}' in df.columns else feat
            if col in df.columns:
                feature_columns.append(col)
        
        # 4. 成交量特征
        volume_features = ['Volume_Change', 'OBV']
        for feat in volume_features:
            col = f'market_{feat}' if f'market_{feat}' in df.columns else feat
            if col in df.columns:
                feature_columns.append(col)
        
        # 5. 移动平均线差值（趋势强度）
        if 'market_MA7' in df.columns and 'market_MA30' in df.columns:
            df['MA_Diff'] = (df['market_MA7'] - df['market_MA30']) / df['market_Close']
            feature_columns.append('MA_Diff')
        
        self.log(f"选择了 {len(feature_columns)} 个特征")
        
        # 提取特征
        X = df[feature_columns].values
        
        # 处理缺失值和无穷值
        X = np.nan_to_num(X, nan=0, posinf=0, neginf=0)
        
        return X, feature_columns
    
    def fit_kmeans(self, X: np.ndarray, random_state: int = 42) -> np.ndarray:
        """
        使用K-Means聚类识别市场状态
        
        Args:
            X: 特征矩阵
            random_state: 随机种子
        
        Returns:
            状态标签数组
        """
        self.log(f"训练 K-Means 模型 (n_clusters={self.n_regimes})...")
        
        # 标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # K-Means聚类
        self.kmeans_model = KMeans(
            n_clusters=self.n_regimes,
            random_state=random_state,
            n_init=50,
            max_iter=500
        )
        
        labels = self.kmeans_model.fit_predict(X_scaled)
        
        self.log(f"K-Means 训练完成")
        self.log(f"  Inertia: {self.kmeans_model.inertia_:.2f}")
        
        return labels
    
    def fit_hmm(self, X: np.ndarray, random_state: int = 42) -> np.ndarray:
        """
        使用Hidden Markov Model识别市场状态
        
        Args:
            X: 特征矩阵
            random_state: 随机种子
        
        Returns:
            状态标签数组
        """
        self.log(f"训练 Hidden Markov Model (n_states={self.n_regimes})...")
        
        # 标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # HMM模型
        self.hmm_model = hmm.GaussianHMM(
            n_components=self.n_regimes,
            covariance_type="full",
            n_iter=200,
            random_state=random_state
        )
        
        # 训练
        self.hmm_model.fit(X_scaled)
        
        # 预测状态序列
        labels = self.hmm_model.predict(X_scaled)
        
        self.log(f"HMM 训练完成")
        self.log(f"  Log Likelihood: {self.hmm_model.score(X_scaled):.2f}")
        
        return labels
    
    def map_regimes_to_meanings(self, df: pd.DataFrame, labels: np.ndarray) -> np.ndarray:
        """
        将聚类标签映射到有意义的市场状态
        
        Args:
            df: 原始DataFrame
            labels: 聚类标签
        
        Returns:
            映射后的标签
        """
        self.log("映射市场状态...")
        
        # 为每个簇计算特征统计
        cluster_stats = []
        for cluster_id in range(self.n_regimes):
            mask = labels == cluster_id
            cluster_data = df[mask]
            
            # 计算关键统计量
            stats = {
                'cluster_id': cluster_id,
                'count': mask.sum(),
                'avg_return': cluster_data.get('market_Return', cluster_data.get('Return', pd.Series([0]))).mean(),
                'avg_volatility': cluster_data.get('market_Volatility_7d', cluster_data.get('Volatility_7d', pd.Series([0]))).mean(),
                'avg_volume_change': cluster_data.get('market_Volume_Change', cluster_data.get('Volume_Change', pd.Series([0]))).mean(),
            }
            cluster_stats.append(stats)
        
        # 转换为DataFrame便于分析
        stats_df = pd.DataFrame(cluster_stats)
        
        # 映射逻辑：
        # - 恐慌(Panic): 高波动 + 负收益
        # - 狂热(Euphoria): 高波动 + 正收益
        # - 趋势(Trending): 中等波动 + 明显收益
        # - 震荡(Consolidation): 低波动
        
        mapping = {}
        
        # 1. 找出高波动的簇
        high_vol_threshold = stats_df['avg_volatility'].quantile(0.6)
        high_vol_clusters = stats_df[stats_df['avg_volatility'] > high_vol_threshold]
        
        if len(high_vol_clusters) >= 2:
            # 高波动 + 负收益 = 恐慌
            panic_candidate = high_vol_clusters.loc[high_vol_clusters['avg_return'].idxmin()]
            mapping[int(panic_candidate['cluster_id'])] = 2  # Panic
            
            # 高波动 + 正收益 = 狂热
            euphoria_candidate = high_vol_clusters.loc[high_vol_clusters['avg_return'].idxmax()]
            mapping[int(euphoria_candidate['cluster_id'])] = 3  # Euphoria
        
        # 2. 剩余簇
        remaining_clusters = stats_df[~stats_df['cluster_id'].isin(mapping.keys())]
        
        if len(remaining_clusters) > 0:
            # 低波动 = 震荡
            consolidation_candidate = remaining_clusters.loc[remaining_clusters['avg_volatility'].idxmin()]
            mapping[int(consolidation_candidate['cluster_id'])] = 0  # Consolidation
            
            # 剩余的 = 趋势
            remaining_clusters = remaining_clusters[remaining_clusters['cluster_id'] != consolidation_candidate['cluster_id']]
            for _, row in remaining_clusters.iterrows():
                mapping[int(row['cluster_id'])] = 1  # Trending
        
        # 保存映射
        self.regime_mapping = mapping
        
        # 应用映射
        mapped_labels = np.array([mapping.get(label, 1) for label in labels])
        
        # 打印映射结果
        self.log("状态映射结果:")
        for old_label, new_label in mapping.items():
            regime_name = self.REGIMES[new_label]
            regime_cn = self.REGIME_CN[new_label]
            count = (labels == old_label).sum()
            self.log(f"  Cluster {old_label} -> {regime_name} ({regime_cn}): {count} 天")
        
        return mapped_labels
    
    def fit(self, df: pd.DataFrame, method: Optional[str] = None) -> pd.DataFrame:
        """
        训练市场状态识别模型
        
        Args:
            df: 输入DataFrame (包含特征)
            method: 识别方法 (如不指定则使用初始化时的方法)
        
        Returns:
            添加了market_regime列的DataFrame
        """
        method = method or self.method
        
        self.log("\n" + "=" * 60)
        self.log(f"开始训练市场状态识别模型 (方法: {method})")
        self.log("=" * 60)
        
        # 准备特征
        X, feature_names = self.prepare_features(df)
        self.log(f"特征矩阵形状: {X.shape}")
        
        # 根据方法选择模型
        if method == 'kmeans':
            labels = self.fit_kmeans(X)
        elif method == 'hmm':
            labels = self.fit_hmm(X)
        elif method == 'hybrid':
            # 混合方法：先用K-Means，再用HMM平滑
            labels_kmeans = self.fit_kmeans(X)
            self.log("使用 HMM 平滑 K-Means 结果...")
            labels = self.fit_hmm(X)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # 映射到有意义的状态
        mapped_labels = self.map_regimes_to_meanings(df, labels)
        
        # 添加到DataFrame
        df_result = df.copy()
        df_result['market_regime'] = mapped_labels
        df_result['market_regime_name'] = [self.REGIMES[label] for label in mapped_labels]
        df_result['market_regime_cn'] = [self.REGIME_CN[label] for label in mapped_labels]
        
        # 统计
        self.log("\n" + "=" * 60)
        self.log("市场状态分布:")
        self.log("=" * 60)
        for regime_id, regime_name in self.REGIMES.items():
            count = (mapped_labels == regime_id).sum()
            pct = count / len(mapped_labels) * 100
            self.log(f"  {regime_name} ({self.REGIME_CN[regime_id]}): {count} 天 ({pct:.1f}%)")
        
        self.log("=" * 60 + "\n")
        
        return df_result
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        预测新数据的市场状态
        
        Args:
            df: 输入DataFrame
        
        Returns:
            状态标签数组
        """
        if self.kmeans_model is None and self.hmm_model is None:
            raise ValueError("模型未训练，请先调用 fit()")
        
        # 准备特征
        X, _ = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # 预测
        if self.method == 'kmeans' and self.kmeans_model is not None:
            labels = self.kmeans_model.predict(X_scaled)
        elif self.method == 'hmm' and self.hmm_model is not None:
            labels = self.hmm_model.predict(X_scaled)
        else:
            raise ValueError("无可用模型进行预测")
        
        # 应用映射
        if self.regime_mapping:
            mapped_labels = np.array([self.regime_mapping.get(label, 1) for label in labels])
        else:
            mapped_labels = labels
        
        return mapped_labels
    
    def analyze_regime_characteristics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        分析各市场状态的特征
        
        Args:
            df: 包含market_regime的DataFrame
        
        Returns:
            特征统计DataFrame
        """
        if 'market_regime' not in df.columns:
            raise ValueError("DataFrame 缺少 market_regime 列")
        
        self.log("分析市场状态特征...")
        
        stats = []
        for regime_id in range(self.n_regimes):
            regime_data = df[df['market_regime'] == regime_id]
            
            if len(regime_data) == 0:
                continue
            
            # 提取关键指标
            stat = {
                'regime': self.REGIMES[regime_id],
                'regime_cn': self.REGIME_CN[regime_id],
                'count': len(regime_data),
                'avg_return': regime_data.get('market_Return', regime_data.get('Return', pd.Series([0]))).mean(),
                'std_return': regime_data.get('market_Return', regime_data.get('Return', pd.Series([0]))).std(),
                'avg_volatility': regime_data.get('market_Volatility_7d', regime_data.get('Volatility_7d', pd.Series([0]))).mean(),
                'avg_rsi': regime_data.get('market_RSI14', regime_data.get('RSI14', pd.Series([0]))).mean(),
                'avg_volume_change': regime_data.get('market_Volume_Change', regime_data.get('Volume_Change', pd.Series([0]))).mean(),
            }
            stats.append(stat)
        
        stats_df = pd.DataFrame(stats)
        
        return stats_df


def main():
    """测试市场状态识别"""
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - Market Regime Identification Test")
    print("=" * 70 + "\n")
    
    # 加载特征数据
    try:
        df = pd.read_csv('data/processed/integrated_features.csv', index_col=0, parse_dates=True)
        print(f"Loaded data: {len(df)} rows, {len(df.columns)} columns")
    except FileNotFoundError:
        print("Error: Please run feature engineering first (WAL-13)")
        return
    
    # 创建识别器
    identifier = MarketRegimeIdentifier(n_regimes=4, method='kmeans', verbose=True)
    
    # 训练模型
    df_with_regime = identifier.fit(df)
    
    # 分析特征
    regime_stats = identifier.analyze_regime_characteristics(df_with_regime)
    
    print("\n" + "=" * 70)
    print("Market Regime Characteristics:")
    print("=" * 70)
    print(regime_stats.to_string(index=False))
    
    # 保存结果
    output_file = 'data/processed/market_regime.csv'
    df_with_regime.to_csv(output_file)
    print(f"\n[SUCCESS] Results saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

