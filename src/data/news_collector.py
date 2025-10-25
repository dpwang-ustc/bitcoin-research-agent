"""
新闻数据收集器

功能：
1. 加密货币相关新闻
2. 宏观经济新闻
3. 政策和监管新闻
4. 市场事件和情绪

数据源：
- NewsAPI (需要 API Key) - 综合新闻
- CryptoPanic API (免费) - 加密货币专门新闻
- RSS Feeds (免费) - CoinDesk, CoinTelegraph 等

依赖：requests, pandas, feedparser
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import os
try:
    import feedparser
except ImportError:
    feedparser = None
    print("⚠️  建议安装 feedparser: pip install feedparser")


class NewsCollector:
    """新闻数据收集器"""
    
    # CryptoPanic API
    CRYPTOPANIC_BASE = "https://cryptopanic.com/api/v1"
    
    # NewsAPI
    NEWSAPI_BASE = "https://newsapi.org/v2"
    
    # RSS Feeds
    RSS_FEEDS = {
        'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'cointelegraph': 'https://cointelegraph.com/rss',
        'decrypt': 'https://decrypt.co/feed',
        'bitcoin_magazine': 'https://bitcoinmagazine.com/.rss/full/',
    }
    
    def __init__(self, 
                 cryptopanic_key: Optional[str] = None,
                 newsapi_key: Optional[str] = None):
        """
        初始化
        
        Args:
            cryptopanic_key: CryptoPanic API Key (免费注册)
            newsapi_key: NewsAPI Key (免费层: 100 requests/day)
        """
        self.cryptopanic_key = cryptopanic_key or os.getenv('CRYPTOPANIC_API_KEY')
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Bitcoin Research Agent)'
        })
    
    # ==================== CryptoPanic API ====================
    
    def get_cryptopanic_news(self,
                            currencies: str = 'BTC',
                            filter_type: str = 'hot',
                            kind: str = 'news',
                            limit: int = 50) -> pd.DataFrame:
        """
        从 CryptoPanic 获取加密货币新闻
        
        Args:
            currencies: 币种代码 (BTC, ETH, 等)
            filter_type: 过滤类型 (hot, rising, bullish, bearish, important, saved, lol)
            kind: 类型 (news, media, all)
            limit: 返回数量
        
        Returns:
            DataFrame with news data
        """
        if not self.cryptopanic_key:
            print("⚠️  需要 CryptoPanic API Key")
            print("   免费注册: https://cryptopanic.com/developers/api/")
            return pd.DataFrame()
        
        endpoint = f"{self.CRYPTOPANIC_BASE}/posts/"
        
        params = {
            'auth_token': self.cryptopanic_key,
            'currencies': currencies,
            'filter': filter_type,
            'kind': kind,
            'public': 'true'
        }
        
        try:
            print(f"正在获取 CryptoPanic 新闻 ({filter_type})...")
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('results', [])
            
            if not posts:
                print("✗ 未获取到新闻")
                return pd.DataFrame()
            
            # 解析新闻数据
            news_list = []
            for post in posts[:limit]:
                news_item = {
                    'id': post.get('id'),
                    'title': post.get('title'),
                    'published_at': pd.to_datetime(post.get('published_at')),
                    'url': post.get('url'),
                    'source': post.get('source', {}).get('title', 'Unknown'),
                    'domain': post.get('domain'),
                    'votes': post.get('votes', {}).get('liked', 0) - post.get('votes', {}).get('disliked', 0),
                    'sentiment': self._determine_sentiment(post),
                    'currencies': ','.join([c['code'] for c in post.get('currencies', [])]),
                }
                news_list.append(news_item)
            
            df = pd.DataFrame(news_list)
            df.set_index('published_at', inplace=True)
            df.sort_index(ascending=False, inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 条 CryptoPanic 新闻")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ CryptoPanic API 请求失败: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"✗ CryptoPanic 数据处理失败: {e}")
            return pd.DataFrame()
    
    def _determine_sentiment(self, post: Dict) -> str:
        """根据 CryptoPanic 的标签判断情感"""
        votes = post.get('votes', {})
        
        # 根据投票判断
        liked = votes.get('liked', 0)
        disliked = votes.get('disliked', 0)
        
        if liked > disliked * 2:
            return 'positive'
        elif disliked > liked * 2:
            return 'negative'
        else:
            return 'neutral'
    
    # ==================== NewsAPI ====================
    
    def get_newsapi_articles(self,
                            query: str = 'bitcoin OR cryptocurrency',
                            from_date: Optional[str] = None,
                            to_date: Optional[str] = None,
                            language: str = 'en',
                            sort_by: str = 'publishedAt',
                            page_size: int = 50) -> pd.DataFrame:
        """
        从 NewsAPI 获取新闻
        
        Args:
            query: 搜索关键词
            from_date: 开始日期 (YYYY-MM-DD)
            to_date: 结束日期 (YYYY-MM-DD)
            language: 语言代码
            sort_by: 排序方式 (publishedAt, relevancy, popularity)
            page_size: 每页数量 (max 100)
        
        Returns:
            DataFrame with articles
        """
        if not self.newsapi_key:
            print("⚠️  需要 NewsAPI Key")
            print("   免费注册: https://newsapi.org/register")
            print("   免费层: 100 requests/day, 1 month历史")
            return pd.DataFrame()
        
        endpoint = f"{self.NEWSAPI_BASE}/everything"
        
        # 默认日期范围（最近7天）
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'from': from_date,
            'to': to_date,
            'language': language,
            'sortBy': sort_by,
            'pageSize': min(page_size, 100),
            'apiKey': self.newsapi_key
        }
        
        try:
            print(f"正在从 NewsAPI 获取新闻...")
            
            response = self.session.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"✗ NewsAPI 返回错误: {data.get('message', 'Unknown')}")
                return pd.DataFrame()
            
            articles = data.get('articles', [])
            
            if not articles:
                print("✗ 未获取到新闻")
                return pd.DataFrame()
            
            # 解析文章
            news_list = []
            for article in articles:
                news_item = {
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'content': article.get('content'),
                    'published_at': pd.to_datetime(article.get('publishedAt')),
                    'url': article.get('url'),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'author': article.get('author'),
                }
                news_list.append(news_item)
            
            df = pd.DataFrame(news_list)
            df.set_index('published_at', inplace=True)
            df.sort_index(ascending=False, inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 条 NewsAPI 文章")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"✗ NewsAPI 请求失败: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"✗ NewsAPI 数据处理失败: {e}")
            return pd.DataFrame()
    
    # ==================== RSS Feeds ====================
    
    def get_rss_feed(self, 
                    feed_name: str,
                    max_entries: int = 50) -> pd.DataFrame:
        """
        从 RSS Feed 获取新闻
        
        Args:
            feed_name: Feed 名称 (coindesk, cointelegraph, etc.)
            max_entries: 最大条目数
        
        Returns:
            DataFrame with feed entries
        """
        if feedparser is None:
            print("✗ 需要安装 feedparser: pip install feedparser")
            return pd.DataFrame()
        
        if feed_name not in self.RSS_FEEDS:
            print(f"✗ 不支持的 RSS Feed: {feed_name}")
            print(f"  支持的 Feed: {', '.join(self.RSS_FEEDS.keys())}")
            return pd.DataFrame()
        
        feed_url = self.RSS_FEEDS[feed_name]
        
        try:
            print(f"正在从 {feed_name.upper()} RSS Feed 获取新闻...")
            
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print(f"✗ {feed_name} RSS Feed 为空")
                return pd.DataFrame()
            
            # 解析条目
            news_list = []
            for entry in feed.entries[:max_entries]:
                # 解析发布时间
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    published_dt = datetime(*published[:6])
                else:
                    published_dt = datetime.now()
                
                news_item = {
                    'title': entry.get('title'),
                    'summary': entry.get('summary', ''),
                    'published_at': published_dt,
                    'url': entry.get('link'),
                    'source': feed_name,
                    'author': entry.get('author', 'Unknown'),
                }
                news_list.append(news_item)
            
            df = pd.DataFrame(news_list)
            df.set_index('published_at', inplace=True)
            df.sort_index(ascending=False, inplace=True)
            
            print(f"✓ 成功获取 {len(df)} 条 {feed_name.upper()} 新闻")
            return df
            
        except Exception as e:
            print(f"✗ RSS Feed 获取失败: {e}")
            return pd.DataFrame()
    
    def get_all_rss_feeds(self, max_entries: int = 30) -> Dict[str, pd.DataFrame]:
        """
        获取所有 RSS Feeds
        
        Args:
            max_entries: 每个 Feed 最大条目数
        
        Returns:
            Dict of DataFrames
        """
        print("=" * 60)
        print("  批量获取 RSS 新闻")
        print("=" * 60)
        print()
        
        result = {}
        
        for feed_name in self.RSS_FEEDS.keys():
            df = self.get_rss_feed(feed_name, max_entries)
            if not df.empty:
                result[feed_name] = df
            time.sleep(1)  # 避免请求过快
        
        print()
        print(f"✓ 共获取 {len(result)}/{len(self.RSS_FEEDS)} 个 RSS Feed")
        return result
    
    # ==================== 综合方法 ====================
    
    def get_comprehensive_news(self,
                              days_back: int = 7,
                              include_cryptopanic: bool = True,
                              include_newsapi: bool = True,
                              include_rss: bool = True) -> Dict[str, pd.DataFrame]:
        """
        获取综合新闻数据
        
        Args:
            days_back: 回溯天数
            include_cryptopanic: 包含 CryptoPanic
            include_newsapi: 包含 NewsAPI
            include_rss: 包含 RSS Feeds
        
        Returns:
            Dict of news DataFrames
        """
        print("=" * 60)
        print("  获取综合新闻数据")
        print("=" * 60)
        print()
        
        result = {}
        
        # 1. CryptoPanic
        if include_cryptopanic and self.cryptopanic_key:
            print("1. CryptoPanic 新闻:")
            
            # 不同过滤类型
            for filter_type in ['hot', 'important']:
                df = self.get_cryptopanic_news(filter_type=filter_type, limit=30)
                if not df.empty:
                    result[f'cryptopanic_{filter_type}'] = df
                time.sleep(1)
            print()
        
        # 2. NewsAPI
        if include_newsapi and self.newsapi_key:
            print("2. NewsAPI 新闻:")
            
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            df = self.get_newsapi_articles(
                query='bitcoin OR cryptocurrency OR blockchain',
                from_date=from_date,
                page_size=50
            )
            if not df.empty:
                result['newsapi'] = df
            print()
        
        # 3. RSS Feeds
        if include_rss:
            print("3. RSS Feeds:")
            
            rss_data = self.get_all_rss_feeds(max_entries=20)
            result.update(rss_data)
        
        print("=" * 60)
        print(f"  共获取 {len(result)} 个新闻源")
        print("=" * 60)
        print()
        
        return result


def main():
    """测试新闻数据收集器"""
    import sys
    import io
    
    # Windows UTF-8 输出
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("  新闻数据收集器测试")
    print("=" * 60)
    print()
    
    collector = NewsCollector()
    
    # 1. 测试 RSS Feeds（无需 API Key）
    print("【测试 1】RSS Feeds (免费)\n")
    
    rss_data = collector.get_all_rss_feeds(max_entries=10)
    
    if rss_data:
        print(f"\n获取的 RSS Feed:")
        for feed_name, df in rss_data.items():
            print(f"\n{feed_name.upper()}:")
            print(f"  - 新闻数: {len(df)}")
            if not df.empty:
                print(f"  - 最新标题: {df['title'].iloc[0]}")
    
    # 2. 测试 CryptoPanic（需要 API Key）
    print("\n【测试 2】CryptoPanic API\n")
    
    if collector.cryptopanic_key:
        cp_news = collector.get_cryptopanic_news(filter_type='hot', limit=10)
        if not cp_news.empty:
            print(f"\nCryptoPanic 热门新闻:")
            print(cp_news[['title', 'source', 'sentiment']].head())
    else:
        print("⚠️  跳过（未设置 CRYPTOPANIC_API_KEY）")
    
    # 3. 测试 NewsAPI（需要 API Key）
    print("\n【测试 3】NewsAPI\n")
    
    if collector.newsapi_key:
        news = collector.get_newsapi_articles(
            query='bitcoin',
            page_size=10
        )
        if not news.empty:
            print(f"\nNewsAPI 文章:")
            print(news[['title', 'source']].head())
    else:
        print("⚠️  跳过（未设置 NEWSAPI_KEY）")
    
    # 4. 保存数据
    print("\n【测试 4】保存数据\n")
    
    os.makedirs('data/raw', exist_ok=True)
    
    saved_count = 0
    for source, df in rss_data.items():
        if not df.empty:
            filename = f'data/raw/news_{source}.csv'
            df.to_csv(filename)
            print(f"✓ {filename}")
            saved_count += 1
    
    print(f"\n✓ 共保存 {saved_count} 个新闻文件")
    
    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("- RSS Feeds 完全免费，无需 API Key")
    print("- CryptoPanic: https://cryptopanic.com/developers/api/")
    print("- NewsAPI: https://newsapi.org/register (免费层 100 次/天)")


if __name__ == "__main__":
    main()

