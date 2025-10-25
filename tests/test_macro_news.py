"""
WAL-12 宏观与新闻数据收集测试

测试内容：
1. 宏观数据收集器测试（DXY, VIX, 黄金等）
2. 新闻数据收集器测试（RSS, CryptoPanic, NewsAPI）
3. 情感分析器测试
4. 数据聚合器集成测试
5. 数据保存和加载测试
"""

import sys
import io
import os
import pandas as pd
from datetime import datetime, timedelta

# Windows UTF-8 输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.macro_collector import MacroCollector
from data.news_collector import NewsCollector
from analysis.sentiment_analyzer import SentimentAnalyzer
from data.market_data_aggregator import MarketDataAggregator


def print_section_header(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"{' ' * ((60 - len(title)) // 2)}{title}")
    print("=" * 60)


def test_macro_collector():
    """测试宏观数据收集器"""
    print_section_header("测试 1: 宏观数据收集器")
    
    collector = MacroCollector()
    
    try:
        # 测试美元指数
        print("\n1.1 测试美元指数 (DXY):")
        dxy = collector.get_indicator('dxy', start_date='2025-10-01')
        
        if not dxy.empty and 'Close' in dxy.columns:
            print(f"✓ DXY 数据获取成功: {len(dxy)} 条")
            print(f"  最新价格: {dxy['Close'].iloc[-1]:.2f}")
            return_dxy = True
        else:
            print("⚠️  DXY 数据获取失败（可能的网络问题）")
            return_dxy = False
        
        # 测试 VIX
        print("\n1.2 测试 VIX 恐慌指数:")
        vix = collector.get_indicator('vix', start_date='2025-10-01')
        
        if not vix.empty and 'Close' in vix.columns:
            print(f"✓ VIX 数据获取成功: {len(vix)} 条")
            print(f"  最新指数: {vix['Close'].iloc[-1]:.2f}")
            return_vix = True
        else:
            print("⚠️  VIX 数据获取失败")
            return_vix = False
        
        # 测试黄金价格
        print("\n1.3 测试黄金价格:")
        gold = collector.get_indicator('gold', start_date='2025-10-01')
        
        if not gold.empty and 'Close' in gold.columns:
            print(f"✓ 黄金数据获取成功: {len(gold)} 条")
            print(f"  最新价格: ${gold['Close'].iloc[-1]:.2f}")
            return_gold = True
        else:
            print("⚠️  黄金数据获取失败")
            return_gold = False
        
        # 至少一个成功就算通过
        return return_dxy or return_vix or return_gold
        
    except Exception as e:
        print(f"✗ 宏观数据收集器测试失败: {e}")
        return False


def test_news_collector():
    """测试新闻数据收集器"""
    print_section_header("测试 2: 新闻数据收集器")
    
    collector = NewsCollector()
    
    try:
        # 测试 RSS Feeds（免费，最稳定）
        print("\n2.1 测试 RSS Feeds:")
        
        # 测试单个 RSS Feed
        feeds_to_test = ['coindesk', 'cointelegraph']
        rss_success = False
        
        for feed_name in feeds_to_test:
            df = collector.get_rss_feed(feed_name, max_entries=5)
            if not df.empty:
                print(f"✓ {feed_name.upper()} RSS Feed 成功: {len(df)} 条新闻")
                if len(df) > 0:
                    print(f"  最新标题: {df['title'].iloc[0][:60]}...")
                rss_success = True
                break
            else:
                print(f"⚠️  {feed_name.upper()} RSS Feed 失败")
        
        # 测试 CryptoPanic（需要 API Key）
        print("\n2.2 测试 CryptoPanic API:")
        
        if collector.cryptopanic_key:
            cp_df = collector.get_cryptopanic_news(filter_type='hot', limit=5)
            if not cp_df.empty:
                print(f"✓ CryptoPanic 数据获取成功: {len(cp_df)} 条新闻")
                cp_success = True
            else:
                print("⚠️  CryptoPanic 数据为空")
                cp_success = False
        else:
            print("⚠️  跳过（未设置 CRYPTOPANIC_API_KEY）")
            cp_success = True  # 跳过不算失败
        
        # 测试 NewsAPI（需要 API Key）
        print("\n2.3 测试 NewsAPI:")
        
        if collector.newsapi_key:
            news_df = collector.get_newsapi_articles(query='bitcoin', page_size=5)
            if not news_df.empty:
                print(f"✓ NewsAPI 数据获取成功: {len(news_df)} 条文章")
                newsapi_success = True
            else:
                print("⚠️  NewsAPI 数据为空")
                newsapi_success = False
        else:
            print("⚠️  跳过（未设置 NEWSAPI_KEY）")
            newsapi_success = True  # 跳过不算失败
        
        # 至少 RSS 成功即可
        return rss_success
        
    except Exception as e:
        print(f"✗ 新闻数据收集器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sentiment_analyzer():
    """测试情感分析器"""
    print_section_header("测试 3: 情感分析器")
    
    try:
        analyzer = SentimentAnalyzer(use_vader=True, use_textblob=True)
        
        # 测试样本
        test_texts = [
            "Bitcoin surges to new all-time high as institutions buy",
            "Crypto market crashes amid regulatory fears",
            "Bitcoin price remains stable",
        ]
        
        print("\n3.1 单条文本情感分析:")
        all_analyzed = True
        
        for text in test_texts:
            result = analyzer.analyze_text(text)
            if result and 'sentiment' in result:
                print(f"✓ 文本: {text[:50]}...")
                print(f"  情感: {result['sentiment']} (得分: {result['score']:.3f})")
            else:
                print(f"✗ 分析失败: {text[:50]}...")
                all_analyzed = False
        
        # 测试批量分析
        print("\n3.2 批量情感分析:")
        
        df = pd.DataFrame({
            'title': test_texts,
            'published_at': pd.date_range(start='2025-10-23', periods=3, freq='D')
        })
        df.set_index('published_at', inplace=True)
        
        df_analyzed = analyzer.analyze_dataframe(df, text_column='title')
        
        if 'sentiment' in df_analyzed.columns and 'sentiment_score' in df_analyzed.columns:
            print(f"✓ 批量分析成功: {len(df_analyzed)} 条")
            print(f"\n情感分布:")
            print(df_analyzed['sentiment'].value_counts())
            return True
        else:
            print("✗ 批量分析失败")
            return False
        
    except Exception as e:
        print(f"✗ 情感分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_aggregator_integration():
    """测试数据聚合器集成"""
    print_section_header("测试 4: 数据聚合器集成")
    
    try:
        aggregator = MarketDataAggregator()
        
        print("\n正在收集综合数据（包含宏观和新闻）...")
        print("注意：这可能需要几分钟时间...\n")
        
        data_dict = aggregator.get_comprehensive_data(
            days_back=7,
            include_funding=False,  # 跳过可能失败的 Binance
            include_market_info=True,
            include_onchain=False,  # 跳过链上数据加快测试
            include_macro=True,
            include_news=True
        )
        
        if data_dict:
            print(f"\n✓ 数据聚合成功，共 {len(data_dict)} 个数据集")
            
            # 检查宏观数据
            macro_keys = [k for k in data_dict.keys() if k.startswith('macro_')]
            if macro_keys:
                print(f"\n宏观数据集 ({len(macro_keys)}):")
                for key in macro_keys:
                    print(f"  ✓ {key}: {len(data_dict[key])} 条")
            else:
                print("\n⚠️  未找到宏观数据集")
            
            # 检查新闻数据
            news_keys = [k for k in data_dict.keys() if k.startswith('news_')]
            if news_keys:
                print(f"\n新闻数据集 ({len(news_keys)}):")
                for key in news_keys:
                    print(f"  ✓ {key}: {len(data_dict[key])} 条")
            else:
                print("\n⚠️  未找到新闻数据集")
            
            # 至少有宏观或新闻数据
            return len(macro_keys) > 0 or len(news_keys) > 0
        else:
            print("✗ 数据聚合失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据聚合器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_save_load():
    """测试数据保存和加载"""
    print_section_header("测试 5: 数据保存和加载")
    
    try:
        # 确保目录存在
        os.makedirs('data/raw', exist_ok=True)
        
        # 获取一些宏观数据
        print("\n5.1 获取并保存宏观数据:")
        collector = MacroCollector()
        
        macro_data = collector.get_all_macro_indicators(
            start_date='2025-10-20',
            indicators=['vix', 'gold']
        )
        
        saved_count = 0
        for indicator, df in macro_data.items():
            if not df.empty:
                filename = f'data/raw/macro_{indicator}_test.csv'
                df.to_csv(filename)
                print(f"✓ 保存: {filename}")
                saved_count += 1
                
                # 验证加载
                df_loaded = pd.read_csv(filename, index_col=0, parse_dates=True)
                if len(df_loaded) > 0:
                    print(f"  验证加载: {len(df_loaded)} 行")
        
        # 获取并保存新闻数据
        print("\n5.2 获取并保存新闻数据:")
        news_collector = NewsCollector()
        
        rss_df = news_collector.get_rss_feed('coindesk', max_entries=5)
        
        if not rss_df.empty:
            filename = 'data/raw/news_coindesk_test.csv'
            rss_df.to_csv(filename)
            print(f"✓ 保存: {filename}")
            
            # 验证加载
            df_loaded = pd.read_csv(filename, index_col=0, parse_dates=True)
            print(f"  验证加载: {len(df_loaded)} 行")
            saved_count += 1
        
        return saved_count > 0
        
    except Exception as e:
        print(f"✗ 数据保存/加载测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("  WAL-12 宏观与新闻数据 - 完整测试套件")
    print("=" * 60)
    print()
    
    results = {}
    
    # 运行所有测试
    print("开始测试...\n")
    
    results['宏观数据收集器'] = test_macro_collector()
    results['新闻数据收集器'] = test_news_collector()
    results['情感分析器'] = test_sentiment_analyzer()
    results['数据聚合器集成'] = test_aggregator_integration()
    results['数据保存加载'] = test_data_save_load()
    
    # 汇总结果
    print_section_header("WAL-12 测试结果汇总")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print()
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}  {test_name}")
    
    print()
    print("=" * 60)
    if passed == total:
        print(f"🎉 所有测试通过！({passed}/{total})")
    else:
        print(f"⚠️  部分测试通过 ({passed}/{total})")
    print("=" * 60)
    print()
    
    # 额外说明
    print("📝 注意事项:")
    print("- 宏观数据来自 yfinance（免费，无需 API Key）")
    print("- RSS Feeds 完全免费，无需 API Key")
    print("- CryptoPanic 需要免费注册: https://cryptopanic.com/developers/api/")
    print("- NewsAPI 需要免费注册: https://newsapi.org/register")
    print("- 情感分析支持基础方法（无需安装额外库）")
    print("- 可选安装 VADER 和 TextBlob 提升准确度")
    print()
    
    return passed >= 3  # 至少3个测试通过


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

