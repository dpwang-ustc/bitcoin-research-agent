"""
Bitcoin Research Agent - 市场状态可视化

功能：
1. 可视化市场状态时间序列
2. 展示不同状态下的价格表现
3. 生成市场状态报告图表

作者：Bitcoin Research Agent Team
日期：2025-10-25
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Optional
import warnings
warnings.filterwarnings('ignore')


class RegimeVisualizer:
    """市场状态可视化器"""
    
    # 状态颜色映射
    REGIME_COLORS = {
        0: '#4CAF50',  # Consolidation - 绿色
        1: '#2196F3',  # Trending - 蓝色
        2: '#F44336',  # Panic - 红色
        3: '#FF9800',  # Euphoria - 橙色
    }
    
    REGIME_NAMES = {
        0: 'Consolidation',
        1: 'Trending',
        2: 'Panic',
        3: 'Euphoria'
    }
    
    def __init__(self, figsize: tuple = (15, 10)):
        """
        初始化可视化器
        
        Args:
            figsize: 图表大小
        """
        self.figsize = figsize
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_price_with_regimes(self, 
                               df: pd.DataFrame,
                               price_col: str = 'market_Close',
                               regime_col: str = 'market_regime',
                               save_path: Optional[str] = None):
        """
        绘制价格走势与市场状态
        
        Args:
            df: 包含价格和状态的DataFrame
            price_col: 价格列名
            regime_col: 状态列名
            save_path: 保存路径
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # 上图：价格走势
        ax1.plot(df.index, df[price_col], linewidth=1.5, color='black', alpha=0.7)
        
        # 按状态着色背景
        for regime_id in df[regime_col].unique():
            regime_mask = df[regime_col] == regime_id
            regime_dates = df[regime_mask].index
            
            for date in regime_dates:
                ax1.axvspan(date, date + pd.Timedelta(days=1), 
                           color=self.REGIME_COLORS[regime_id], alpha=0.3)
        
        ax1.set_ylabel('Price (USD)', fontsize=12, fontweight='bold')
        ax1.set_title('Bitcoin Price with Market Regimes', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(['BTC Price'], loc='upper left')
        
        # 下图：市场状态条形图
        colors = [self.REGIME_COLORS[r] for r in df[regime_col]]
        ax2.bar(df.index, [1]*len(df), color=colors, width=1, edgecolor='none')
        ax2.set_ylabel('Regime', fontsize=12, fontweight='bold')
        ax2.set_yticks([])
        ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=self.REGIME_COLORS[i], 
                                label=self.REGIME_NAMES[i]) 
                          for i in sorted(df[regime_col].unique())]
        ax2.legend(handles=legend_elements, loc='upper left', ncol=4)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[SUCCESS] Chart saved to: {save_path}")
        
        plt.close()
    
    def plot_regime_statistics(self,
                              df: pd.DataFrame,
                              regime_col: str = 'market_regime',
                              save_path: Optional[str] = None):
        """
        绘制市场状态统计图
        
        Args:
            df: DataFrame
            regime_col: 状态列名
            save_path: 保存路径
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        
        # 1. 状态分布饼图
        regime_counts = df[regime_col].value_counts().sort_index()
        colors = [self.REGIME_COLORS[i] for i in regime_counts.index]
        labels = [self.REGIME_NAMES[i] for i in regime_counts.index]
        
        axes[0, 0].pie(regime_counts.values, labels=labels, colors=colors,
                      autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Market Regime Distribution', fontweight='bold')
        
        # 2. 各状态平均收益
        avg_returns = []
        regime_labels = []
        for regime_id in sorted(df[regime_col].unique()):
            regime_data = df[df[regime_col] == regime_id]
            return_col = 'market_Return' if 'market_Return' in df.columns else 'Return'
            if return_col in regime_data.columns:
                avg_return = regime_data[return_col].mean() * 100
                avg_returns.append(avg_return)
                regime_labels.append(self.REGIME_NAMES[regime_id])
        
        colors_bar = [self.REGIME_COLORS[i] for i in sorted(df[regime_col].unique())]
        axes[0, 1].bar(regime_labels, avg_returns, color=colors_bar)
        axes[0, 1].set_title('Average Return by Regime', fontweight='bold')
        axes[0, 1].set_ylabel('Return (%)')
        axes[0, 1].axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. 各状态波动率
        avg_vols = []
        for regime_id in sorted(df[regime_col].unique()):
            regime_data = df[df[regime_col] == regime_id]
            vol_col = 'market_Volatility_7d' if 'market_Volatility_7d' in df.columns else 'Volatility_7d'
            if vol_col in regime_data.columns:
                avg_vol = regime_data[vol_col].mean() * 100
                avg_vols.append(avg_vol)
        
        axes[1, 0].bar(regime_labels, avg_vols, color=colors_bar)
        axes[1, 0].set_title('Average Volatility by Regime', fontweight='bold')
        axes[1, 0].set_ylabel('Volatility (%)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. 各状态RSI
        avg_rsis = []
        for regime_id in sorted(df[regime_col].unique()):
            regime_data = df[df[regime_col] == regime_id]
            rsi_col = 'market_RSI14' if 'market_RSI14' in df.columns else 'RSI14'
            if rsi_col in regime_data.columns:
                avg_rsi = regime_data[rsi_col].mean()
                avg_rsis.append(avg_rsi)
        
        axes[1, 1].bar(regime_labels, avg_rsis, color=colors_bar)
        axes[1, 1].set_title('Average RSI by Regime', fontweight='bold')
        axes[1, 1].set_ylabel('RSI')
        axes[1, 1].axhline(y=50, color='black', linestyle='--', linewidth=0.5)
        axes[1, 1].axhline(y=30, color='red', linestyle=':', linewidth=0.5, alpha=0.5)
        axes[1, 1].axhline(y=70, color='green', linestyle=':', linewidth=0.5, alpha=0.5)
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[SUCCESS] Chart saved to: {save_path}")
        
        plt.close()
    
    def plot_regime_transitions(self,
                               df: pd.DataFrame,
                               regime_col: str = 'market_regime',
                               save_path: Optional[str] = None):
        """
        绘制市场状态转移矩阵
        
        Args:
            df: DataFrame
            regime_col: 状态列名
            save_path: 保存路径
        """
        # 计算转移矩阵
        n_regimes = df[regime_col].nunique()
        transition_matrix = np.zeros((n_regimes, n_regimes))
        
        regimes = df[regime_col].values
        for i in range(len(regimes) - 1):
            from_regime = regimes[i]
            to_regime = regimes[i + 1]
            transition_matrix[from_regime, to_regime] += 1
        
        # 归一化
        row_sums = transition_matrix.sum(axis=1, keepdims=True)
        transition_matrix = np.divide(transition_matrix, row_sums, 
                                     where=row_sums!=0, 
                                     out=np.zeros_like(transition_matrix))
        
        # 绘制热图
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(transition_matrix, cmap='YlOrRd', aspect='auto')
        
        # 设置标签
        regime_names = [self.REGIME_NAMES[i] for i in range(n_regimes)]
        ax.set_xticks(np.arange(n_regimes))
        ax.set_yticks(np.arange(n_regimes))
        ax.set_xticklabels(regime_names)
        ax.set_yticklabels(regime_names)
        
        # 旋转标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        
        # 添加数值
        for i in range(n_regimes):
            for j in range(n_regimes):
                text = ax.text(j, i, f'{transition_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_title('Market Regime Transition Matrix', fontweight='bold', fontsize=14)
        ax.set_xlabel('To Regime', fontweight='bold')
        ax.set_ylabel('From Regime', fontweight='bold')
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Transition Probability', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[SUCCESS] Chart saved to: {save_path}")
        
        plt.close()
    
    def generate_all_plots(self,
                          df: pd.DataFrame,
                          output_dir: str = 'data/processed/plots'):
        """
        生成所有可视化图表
        
        Args:
            df: DataFrame
            output_dir: 输出目录
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "=" * 70)
        print("Generating Market Regime Visualization...")
        print("=" * 70)
        
        # 1. 价格与状态
        print("\n1. Plotting price with regimes...")
        self.plot_price_with_regimes(df, save_path=f'{output_dir}/price_with_regimes.png')
        
        # 2. 状态统计
        print("\n2. Plotting regime statistics...")
        self.plot_regime_statistics(df, save_path=f'{output_dir}/regime_statistics.png')
        
        # 3. 状态转移
        print("\n3. Plotting regime transitions...")
        self.plot_regime_transitions(df, save_path=f'{output_dir}/regime_transitions.png')
        
        print("\n" + "=" * 70)
        print(f"All plots saved to: {output_dir}/")
        print("=" * 70 + "\n")


def main():
    """测试可视化"""
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - Regime Visualization Test")
    print("=" * 70 + "\n")
    
    # 加载数据
    try:
        df = pd.read_csv('data/processed/market_regime.csv', index_col=0, parse_dates=True)
        print(f"Loaded data: {len(df)} rows")
    except FileNotFoundError:
        print("Error: Please run market_regime.py first")
        return
    
    # 创建可视化器
    visualizer = RegimeVisualizer(figsize=(15, 10))
    
    # 生成所有图表
    visualizer.generate_all_plots(df)
    
    print("Visualization test completed successfully!")


if __name__ == '__main__':
    main()

