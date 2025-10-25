"""
新闻情感分析器

功能：
1. 文本情感分类（正面/中性/负面）
2. 情感得分计算
3. 关键词提取
4. 批量情感分析

方法：
- 基于词典的情感分析（无需训练模型）
- 加密货币特定关键词
- 支持英文和简单中文

依赖：pandas, numpy
可选：textblob, vaderSentiment (pip install textblob vaderSentiment)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import re


class SentimentAnalyzer:
    """新闻情感分析器"""
    
    # 加密货币特定的正面词汇
    POSITIVE_KEYWORDS = {
        'bullish', 'bull', 'rally', 'surge', 'soar', 'moon', 'pump',
        'breakthrough', 'milestone', 'adoption', 'institutional',
        'approve', 'approved', 'approval', 'launch', 'launched',
        'partnership', 'collaborate', 'integration', 'upgrade',
        'innovation', 'breakthrough', 'record', 'high', 'ath',
        'positive', 'optimistic', 'confidence', 'strong', 'growth',
        'gain', 'increase', 'rise', 'up', 'outperform', 'momentum'
    }
    
    # 负面词汇
    NEGATIVE_KEYWORDS = {
        'bearish', 'bear', 'crash', 'plunge', 'dump', 'collapse',
        'decline', 'fall', 'drop', 'correction', 'selloff', 'sell-off',
        'ban', 'banned', 'restrict', 'regulation', 'crackdown',
        'hack', 'hacked', 'exploit', 'scam', 'fraud', 'ponzi',
        'bubble', 'overvalued', 'risk', 'concern', 'worry', 'fear',
        'panic', 'crisis', 'problem', 'issue', 'lawsuit', 'sue',
        'negative', 'pessimistic', 'weak', 'loss', 'lose', 'down'
    }
    
    # 强调词（放大情感）
    INTENSIFIERS = {
        'very', 'extremely', 'highly', 'significantly', 'massively',
        'huge', 'enormous', 'incredible', 'dramatic', 'major'
    }
    
    # 否定词（反转情感）
    NEGATIONS = {
        'not', 'no', 'never', 'none', 'nobody', 'nothing', 
        'neither', 'nowhere', 'isn\'t', 'aren\'t', 'wasn\'t',
        'weren\'t', 'hasn\'t', 'haven\'t', 'hadn\'t', 'doesn\'t',
        'don\'t', 'didn\'t', 'won\'t', 'wouldn\'t', 'can\'t', 'cannot'
    }
    
    def __init__(self, use_vader: bool = True, use_textblob: bool = True):
        """
        初始化
        
        Args:
            use_vader: 使用 VADER 情感分析（需要安装）
            use_textblob: 使用 TextBlob（需要安装）
        """
        self.use_vader = use_vader
        self.use_textblob = use_textblob
        
        # 尝试加载 VADER
        self.vader = None
        if use_vader:
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                self.vader = SentimentIntensityAnalyzer()
                print("✓ VADER 情感分析器已加载")
            except ImportError:
                print("⚠️  VADER 未安装，使用基础情感分析")
                print("   安装: pip install vaderSentiment")
        
        # 尝试加载 TextBlob
        self.textblob = None
        if use_textblob:
            try:
                from textblob import TextBlob
                self.textblob = TextBlob
                print("✓ TextBlob 已加载")
            except ImportError:
                print("⚠️  TextBlob 未安装，使用基础情感分析")
                print("   安装: pip install textblob")
    
    def analyze_text(self, text: str) -> Dict:
        """
        分析单条文本情感
        
        Args:
            text: 输入文本
        
        Returns:
            Dict with sentiment analysis results
        """
        if not text or not isinstance(text, str):
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'method': 'none'
            }
        
        # 清理文本
        text_clean = self._clean_text(text)
        
        results = []
        
        # 1. 基于关键词的分析（始终运行）
        keyword_result = self._keyword_sentiment(text_clean)
        results.append(keyword_result)
        
        # 2. VADER 分析
        if self.vader:
            vader_result = self._vader_sentiment(text_clean)
            results.append(vader_result)
        
        # 3. TextBlob 分析
        if self.textblob:
            textblob_result = self._textblob_sentiment(text_clean)
            results.append(textblob_result)
        
        # 综合结果
        final_result = self._ensemble_sentiment(results)
        
        return final_result
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 转小写
        text = text.lower()
        # 移除 URL
        text = re.sub(r'http\S+|www.\S+', '', text)
        # 移除特殊字符（保留基本标点）
        text = re.sub(r'[^\w\s\.\,\!\?]', ' ', text)
        # 移除多余空格
        text = ' '.join(text.split())
        return text
    
    def _keyword_sentiment(self, text: str) -> Dict:
        """基于关键词的情感分析"""
        words = set(text.split())
        
        # 计算正负词数量
        positive_count = len(words & self.POSITIVE_KEYWORDS)
        negative_count = len(words & self.NEGATIVE_KEYWORDS)
        
        # 检查否定词
        has_negation = len(words & self.NEGATIONS) > 0
        
        # 检查强调词
        has_intensifier = len(words & self.INTENSIFIERS) > 0
        intensifier_factor = 1.5 if has_intensifier else 1.0
        
        # 计算得分
        if has_negation:
            # 否定词反转情感
            score = (negative_count - positive_count) * intensifier_factor
        else:
            score = (positive_count - negative_count) * intensifier_factor
        
        # 归一化到 [-1, 1]
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words > 0:
            score = score / max(total_sentiment_words, 5)  # 至少除以5避免过度
            score = max(-1.0, min(1.0, score))
        else:
            score = 0.0
        
        # 确定情感
        if score > 0.1:
            sentiment = 'positive'
        elif score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        confidence = abs(score) if total_sentiment_words > 0 else 0.0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'method': 'keyword'
        }
    
    def _vader_sentiment(self, text: str) -> Dict:
        """VADER 情感分析"""
        scores = self.vader.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': compound,
            'confidence': abs(compound),
            'method': 'vader'
        }
    
    def _textblob_sentiment(self, text: str) -> Dict:
        """TextBlob 情感分析"""
        blob = self.textblob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': polarity,
            'confidence': abs(polarity),
            'method': 'textblob'
        }
    
    def _ensemble_sentiment(self, results: List[Dict]) -> Dict:
        """综合多个情感分析结果"""
        if not results:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'method': 'none'
            }
        
        # 加权平均（VADER 和 TextBlob 权重更高）
        weights = {
            'keyword': 0.3,
            'vader': 0.4,
            'textblob': 0.3
        }
        
        total_weight = sum(weights.get(r['method'], 0.3) for r in results)
        weighted_score = sum(r['score'] * weights.get(r['method'], 0.3) for r in results) / total_weight
        
        # 投票决定情感
        sentiment_votes = [r['sentiment'] for r in results]
        sentiment = max(set(sentiment_votes), key=sentiment_votes.count)
        
        # 平均置信度
        confidence = np.mean([r['confidence'] for r in results])
        
        methods = '+'.join([r['method'] for r in results])
        
        return {
            'sentiment': sentiment,
            'score': float(weighted_score),
            'confidence': float(confidence),
            'method': methods
        }
    
    def analyze_dataframe(self, 
                         df: pd.DataFrame,
                         text_column: str = 'title',
                         add_columns: bool = True) -> pd.DataFrame:
        """
        批量分析 DataFrame 中的文本
        
        Args:
            df: 输入 DataFrame
            text_column: 文本列名
            add_columns: 是否添加情感分析列
        
        Returns:
            DataFrame with sentiment columns
        """
        if df.empty or text_column not in df.columns:
            print(f"✗ DataFrame 为空或缺少列: {text_column}")
            return df
        
        print(f"正在分析 {len(df)} 条文本...")
        
        # 批量分析
        sentiments = []
        for idx, text in enumerate(df[text_column]):
            result = self.analyze_text(str(text))
            sentiments.append(result)
            
            if (idx + 1) % 10 == 0:
                print(f"  处理进度: {idx + 1}/{len(df)}")
        
        # 转换为 DataFrame
        sentiment_df = pd.DataFrame(sentiments)
        
        if add_columns:
            # 添加到原 DataFrame
            result_df = df.copy()
            result_df['sentiment'] = sentiment_df['sentiment']
            result_df['sentiment_score'] = sentiment_df['score']
            result_df['sentiment_confidence'] = sentiment_df['confidence']
            
            print(f"✓ 情感分析完成")
            return result_df
        else:
            return sentiment_df
    
    def aggregate_sentiment(self, 
                          df: pd.DataFrame,
                          time_window: str = 'D') -> pd.DataFrame:
        """
        聚合时间窗口内的情感
        
        Args:
            df: 包含情感分析的 DataFrame
            time_window: 时间窗口 (D=天, W=周, M=月)
        
        Returns:
            Aggregated DataFrame
        """
        if 'sentiment_score' not in df.columns:
            print("✗ DataFrame 缺少 sentiment_score 列")
            return pd.DataFrame()
        
        # 按时间窗口聚合
        agg_df = df.resample(time_window).agg({
            'sentiment_score': ['mean', 'std', 'count'],
            'sentiment': lambda x: x.mode()[0] if len(x) > 0 else 'neutral'
        })
        
        agg_df.columns = ['_'.join(col).strip() for col in agg_df.columns.values]
        agg_df.columns = ['avg_sentiment', 'sentiment_volatility', 'news_count', 'dominant_sentiment']
        
        return agg_df


def main():
    """测试情感分析器"""
    import sys
    import io
    
    # Windows UTF-8 输出
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("  情感分析器测试")
    print("=" * 60)
    print()
    
    analyzer = SentimentAnalyzer(use_vader=True, use_textblob=True)
    
    # 测试文本
    test_texts = [
        "Bitcoin surges to new all-time high as institutions show strong bullish sentiment",
        "Cryptocurrency market crashes amid regulatory crackdown fears",
        "Bitcoin price remains stable as traders await next move",
        "Major partnership announced: Bitcoin adoption reaches new milestone",
        "Experts warn of potential bubble in crypto markets",
    ]
    
    print("【测试 1】单条文本分析\n")
    
    for text in test_texts:
        result = analyzer.analyze_text(text)
        print(f"文本: {text}")
        print(f"情感: {result['sentiment']} (得分: {result['score']:.3f}, 置信度: {result['confidence']:.3f})")
        print(f"方法: {result['method']}")
        print()
    
    # 测试 DataFrame
    print("\n【测试 2】批量分析\n")
    
    df = pd.DataFrame({
        'title': test_texts,
        'published_at': pd.date_range(start='2025-10-20', periods=5, freq='D')
    })
    df.set_index('published_at', inplace=True)
    
    df_analyzed = analyzer.analyze_dataframe(df, text_column='title')
    
    print("\n分析结果:")
    print(df_analyzed[['title', 'sentiment', 'sentiment_score']])
    
    # 测试聚合
    print("\n【测试 3】情感聚合\n")
    
    agg_df = analyzer.aggregate_sentiment(df_analyzed, time_window='D')
    print("\n每日情感聚合:")
    print(agg_df)
    
    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

