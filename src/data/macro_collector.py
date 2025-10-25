"""
宏观数据收集器

功能：
1. 美元指数 (DXY) - 衡量美元强弱
2. VIX 恐慌指数 - 市场波动率
3. 黄金价格 - 避险资产
4. 标普500指数 (S&P 500) - 美股市场
5. 美国10年期国债收益率 - 无风险利率

数据源：
- yfinance (免费)
- Federal Reserve Economic Data (FRED) API (可选)

依赖：yfinance, pandas, requests
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import requests
import os
import time


class MacroCollector:
    """宏观数据收集器"""
    
    # 常用宏观指标 Ticker 符号
    TICKERS = {
        'dxy': 'DX-Y.NYB',        # 美元指数
        'vix': '^VIX',             # VIX 波动率指数
        'gold': 'GC=F',            # 黄金期货
        'sp500': '^GSPC',          # 标普500
        'nasdaq': '^IXIC',         # 纳斯达克
        'treasury_10y': '^TNX',    # 10年期国债收益率
        'oil': 'CL=F',             # 原油期货
        'silver': 'SI=F'           # 白银期货
    }
    
    def __init__(self, fred_api_key: Optional[str] = None):
        """
        初始化
        
        Args:
            fred_api_key: FRED API Key (可选)
        """
        self.fred_api_key = fred_api_key or os.getenv('FRED_API_KEY')
        self.fred_base_url = "https://api.stlouisfed.org/fred/series/observations"
        
    def get_indicator(self, 
                     indicator: str, 
                     start_date: Optional[str] = None, 
                     end_date: Optional[str] = None,
                     period: str = '1d') -> pd.DataFrame:
        """
        获取单个宏观指标数据
        
        Args:
            indicator: 指标名称 (dxy, vix, gold, sp500, nasdaq, treasury_10y)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            period: 数据周期 (1d, 1wk, 1mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        if indicator not in self.TICKERS:
            print(f"✗ 不支持的指标: {indicator}")
            print(f"  支持的指标: {', '.join(self.TICKERS.keys())}")
            return pd.DataFrame()
        
        ticker = self.TICKERS[indicator]
        
        try:
            # 默认日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            print(f"正在获取 {indicator.upper()} 数据...")
            
            # 使用 yfinance 获取数据
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval=period,
                progress=False
            )
            
            if data.empty:
                print(f"✗ {indicator.upper()} 数据为空")
                return pd.DataFrame()
            
            # 标准化列名
            data.columns = [col if isinstance(col, str) else col[0] for col in data.columns]
            
            print(f"✓ 成功获取 {len(data)} 条 {indicator.upper()} 数据")
            return data
            
        except Exception as e:
            print(f"✗ 获取 {indicator.upper()} 数据失败: {e}")
            return pd.DataFrame()
    
    def get_all_macro_indicators(self,
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None,
                                 indicators: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """
        批量获取宏观指标数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            indicators: 指标列表 (None = 全部)
        
        Returns:
            Dict of DataFrames
        """
        if indicators is None:
            indicators = ['dxy', 'vix', 'gold', 'sp500', 'treasury_10y']
        
        print("=" * 60)
        print("  批量获取宏观数据")
        print("=" * 60)
        print()
        
        result = {}
        
        for indicator in indicators:
            df = self.get_indicator(indicator, start_date, end_date)
            if not df.empty:
                result[indicator] = df
            time.sleep(0.5)  # 避免请求过快
        
        print()
        print(f"✓ 共获取 {len(result)}/{len(indicators)} 个指标数据")
        return result
    
    def get_fred_data(self, 
                     series_id: str,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> pd.DataFrame:
        """
        从 FRED 获取经济数据
        
        常用 Series ID:
        - DGS10: 10年期国债收益率
        - DEXUSEU: 美元/欧元汇率
        - DEXJPUS: 美元/日元汇率
        - UNRATE: 失业率
        - CPIAUCSL: CPI 消费者价格指数
        
        Args:
            series_id: FRED 系列 ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            DataFrame with time series data
        """
        if not self.fred_api_key:
            print("⚠️  需要 FRED API Key")
            print("   注册: https://fred.stlouisfed.org/docs/api/api_key.html")
            return pd.DataFrame()
        
        try:
            params = {
                'series_id': series_id,
                'api_key': self.fred_api_key,
                'file_type': 'json'
            }
            
            if start_date:
                params['observation_start'] = start_date
            if end_date:
                params['observation_end'] = end_date
            
            print(f"正在从 FRED 获取 {series_id} 数据...")
            
            response = requests.get(self.fred_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            observations = data.get('observations', [])
            
            if not observations:
                print(f"✗ {series_id} 数据为空")
                return pd.DataFrame()
            
            # 转换为 DataFrame
            df = pd.DataFrame(observations)
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df[['date', 'value']].set_index('date')
            df.columns = [series_id]
            
            print(f"✓ 成功获取 {len(df)} 条 FRED 数据")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ FRED API 请求失败: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"✗ FRED 数据处理失败: {e}")
            return pd.DataFrame()
    
    def merge_with_bitcoin(self, 
                          macro_data: Dict[str, pd.DataFrame],
                          bitcoin_df: pd.DataFrame) -> pd.DataFrame:
        """
        将宏观数据与比特币数据合并
        
        Args:
            macro_data: 宏观数据字典
            bitcoin_df: 比特币价格 DataFrame
        
        Returns:
            Merged DataFrame
        """
        print("\n正在合并宏观数据与比特币数据...")
        
        result = bitcoin_df.copy()
        
        for indicator, df in macro_data.items():
            if df.empty:
                continue
            
            # 只保留收盘价
            if 'Close' in df.columns:
                col_name = f'{indicator}_close'
                result = result.join(df[['Close']].rename(columns={'Close': col_name}), how='left')
                print(f"  ✓ 合并 {indicator.upper()}")
        
        # 前向填充缺失值（因为宏观数据可能不是每日更新）
        result.ffill(inplace=True)
        
        print(f"\n✓ 合并完成: {result.shape[0]} 行 x {result.shape[1]} 列")
        return result
    
    def get_macro_snapshot(self) -> Dict:
        """
        获取当前宏观数据快照
        
        Returns:
            Dict with latest values
        """
        print("\n获取宏观数据快照...")
        
        snapshot = {}
        
        # 获取最近一天的数据
        for indicator in ['dxy', 'vix', 'gold', 'sp500', 'treasury_10y']:
            df = self.get_indicator(indicator, period='1d')
            if not df.empty and 'Close' in df.columns:
                snapshot[indicator] = {
                    'value': df['Close'].iloc[-1],
                    'timestamp': df.index[-1]
                }
            time.sleep(0.3)
        
        return snapshot


def main():
    """测试宏观数据收集器"""
    print("=" * 60)
    print("  宏观数据收集器测试")
    print("=" * 60)
    print()
    
    collector = MacroCollector()
    
    # 1. 测试单个指标
    print("【测试 1】获取单个指标\n")
    
    # 美元指数
    dxy = collector.get_indicator('dxy', start_date='2024-01-01')
    if not dxy.empty:
        print(f"\n美元指数 (DXY) 最近数据:")
        print(dxy.tail())
    
    print("\n" + "-" * 60 + "\n")
    
    # VIX 恐慌指数
    vix = collector.get_indicator('vix', start_date='2024-01-01')
    if not vix.empty:
        print(f"\nVIX 恐慌指数最近数据:")
        print(vix.tail())
    
    print("\n" + "-" * 60 + "\n")
    
    # 黄金价格
    gold = collector.get_indicator('gold', start_date='2024-01-01')
    if not gold.empty:
        print(f"\n黄金价格最近数据:")
        print(gold.tail())
    
    # 2. 批量获取
    print("\n【测试 2】批量获取宏观数据\n")
    
    macro_data = collector.get_all_macro_indicators(
        start_date='2024-10-01',
        indicators=['dxy', 'vix', 'gold', 'sp500']
    )
    
    print(f"\n获取的指标:")
    for indicator, df in macro_data.items():
        print(f"  - {indicator.upper()}: {len(df)} 条数据")
    
    # 3. 宏观数据快照
    print("\n【测试 3】获取当前宏观数据快照\n")
    
    snapshot = collector.get_macro_snapshot()
    
    print("\n当前宏观数据:")
    for indicator, info in snapshot.items():
        print(f"  {indicator.upper()}: {info['value']:.2f} (更新: {info['timestamp']})")
    
    # 4. 保存数据
    print("\n【测试 4】保存数据\n")
    
    os.makedirs('data/raw', exist_ok=True)
    
    for indicator, df in macro_data.items():
        if not df.empty:
            filename = f'data/raw/macro_{indicator}.csv'
            df.to_csv(filename)
            print(f"✓ {filename}")
    
    # 保存快照
    if snapshot:
        snapshot_df = pd.DataFrame(snapshot).T
        snapshot_df.to_csv('data/raw/macro_snapshot.csv')
        print(f"✓ data/raw/macro_snapshot.csv")
    
    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("- 所有数据均来自 yfinance（免费）")
    print("- 支持日、周、月等不同周期")
    print("- 可通过 FRED API 获取更多经济指标")


if __name__ == "__main__":
    main()

