"""
Bitcoin Research Agent - AI Agent 测试脚本

测试 MarketInsightAgent 的各项功能
"""

import sys
import io
import os

# Force UTF-8 output for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.model.agent_reasoner import MarketInsightAgent


def test_agent_initialization():
    """测试 Agent 初始化"""
    print("\n" + "=" * 70)
    print("测试 1: Agent 初始化")
    print("=" * 70)
    
    try:
        # 尝试使用 OpenAI
        print("\n尝试初始化 OpenAI Agent...")
        agent = MarketInsightAgent(
            provider="openai",
            model="gpt-4o-mini",
            verbose=True
        )
        print("✅ OpenAI Agent 初始化成功")
        return agent
        
    except Exception as e:
        print(f"❌ OpenAI Agent 初始化失败: {e}")
        print("\n提示: 请设置 OPENAI_API_KEY 环境变量")
        print("  export OPENAI_API_KEY=your-key")
        return None


def test_market_analysis(agent):
    """测试市场分析功能"""
    if not agent:
        print("\n⏭️  跳过市场分析测试（Agent 未初始化）")
        return
    
    print("\n" + "=" * 70)
    print("测试 2: 市场数据分析")
    print("=" * 70)
    
    # 模拟市场数据
    mock_stats = {
        'price': {
            'current': 67500,
            'week_start': 65000,
            'week_high': 68000,
            'week_low': 64500,
            'week_return': 3.85,
            'prev_week_close': 65000,
            'week_change': 3.85
        },
        'regime': {
            'current_regime': '趋势',
            'prev_regime': '震荡',
            'regime_changed': True,
            'regime_distribution': {
                '趋势': 60.0,
                '震荡': 30.0,
                '恐慌': 10.0
            }
        },
        'volatility': {
            'current': 45.5,
            'average': 43.2,
            'previous': 42.0,
            'change': 3.5,
            'change_pct': 8.3
        },
        'sentiment': {
            'current': 68,
            'average': 65,
            'previous': 62,
            'current_category': '贪婪',
            'prev_category': '中性',
            'change': 6
        },
        'capital': {
            'main_behavior': '吸筹',
            'whale_count': 15,
            'whale_change': 5,
            'inflow_count': 8,
            'outflow_count': 3,
            'behavior_distribution': {
                '吸筹': 50.0,
                '横盘': 30.0,
                '派发': 20.0
            }
        }
    }
    
    try:
        print("\n生成市场分析...")
        analysis = agent.analyze_market_data(mock_stats)
        
        print("\n📊 AI 市场分析结果：")
        print("-" * 70)
        print(analysis)
        print("-" * 70)
        print("✅ 市场分析测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 市场分析测试失败: {e}")
        return False


def test_executive_summary(agent):
    """测试执行摘要生成"""
    if not agent:
        print("\n⏭️  跳过执行摘要测试（Agent 未初始化）")
        return
    
    print("\n" + "=" * 70)
    print("测试 3: 执行摘要生成")
    print("=" * 70)
    
    mock_stats = {
        'price': {
            'current': 67500,
            'week_return': 3.85
        },
        'regime': {
            'current_regime': '趋势'
        },
        'sentiment': {
            'current': 68,
            'current_category': '贪婪'
        },
        'capital': {
            'main_behavior': '吸筹'
        }
    }
    
    try:
        print("\n生成执行摘要...")
        summary = agent.generate_executive_summary(mock_stats)
        
        print("\n📝 AI 执行摘要：")
        print("-" * 70)
        print(summary)
        print("-" * 70)
        print("✅ 执行摘要测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 执行摘要测试失败: {e}")
        return False


def test_outlook_generation(agent):
    """测试展望生成"""
    if not agent:
        print("\n⏭️  跳过展望生成测试（Agent 未初始化）")
        return
    
    print("\n" + "=" * 70)
    print("测试 4: 下周展望生成")
    print("=" * 70)
    
    mock_stats = {
        'price': {
            'current': 67500,
            'week_return': 3.85,
            'week_high': 68000,
            'week_low': 64500
        },
        'regime': {
            'current_regime': '趋势'
        },
        'sentiment': {
            'current': 68,
            'current_category': '贪婪'
        },
        'capital': {
            'main_behavior': '吸筹'
        },
        'volatility': {
            'current': 45.5
        }
    }
    
    try:
        print("\n生成下周展望...")
        outlook = agent.generate_outlook(mock_stats)
        
        print("\n🔮 AI 下周展望：")
        print("-" * 70)
        print(outlook)
        print("-" * 70)
        print("✅ 展望生成测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 展望生成测试失败: {e}")
        return False


def test_full_report(agent):
    """测试完整报告生成"""
    if not agent:
        print("\n⏭️  跳过完整报告测试（Agent 未初始化）")
        return
    
    print("\n" + "=" * 70)
    print("测试 5: 完整叙事性报告生成")
    print("=" * 70)
    
    mock_stats = {
        'price': {
            'current': 67500,
            'week_start': 65000,
            'week_high': 68000,
            'week_low': 64500,
            'week_return': 3.85,
            'prev_week_close': 65000
        },
        'regime': {
            'current_regime': '趋势',
            'prev_regime': '震荡',
            'regime_changed': True,
            'regime_distribution': {'趋势': 60.0, '震荡': 30.0}
        },
        'volatility': {
            'current': 45.5,
            'change': 3.5
        },
        'sentiment': {
            'current': 68,
            'current_category': '贪婪',
            'change': 6
        },
        'capital': {
            'main_behavior': '吸筹',
            'whale_count': 15,
            'inflow_count': 8,
            'outflow_count': 3
        }
    }
    
    try:
        print("\n生成完整报告...")
        report = agent.generate_narrative_report(mock_stats)
        
        print("\n📊 完整 AI 报告：")
        print("=" * 70)
        
        print("\n【执行摘要】")
        print(report['executive_summary'])
        
        print("\n" + "-" * 70)
        print("\n【市场分析】")
        print(report['market_analysis'])
        
        print("\n" + "-" * 70)
        print("\n【下周展望】")
        print(report['outlook'])
        
        print("\n" + "=" * 70)
        print("✅ 完整报告测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整报告测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("  Bitcoin Research Agent - AI Agent 测试")
    print("=" * 70)
    
    print("\n📝 测试说明:")
    print("1. 需要设置 OPENAI_API_KEY 环境变量")
    print("2. 如果没有 API key，测试将跳过")
    print("3. 也可以使用 Ollama 本地模型（需先启动 ollama serve）")
    
    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  警告: 未检测到 OPENAI_API_KEY 环境变量")
        print("测试将尝试运行，但可能失败")
    
    # 运行测试
    results = {}
    
    # 测试 1: 初始化
    agent = test_agent_initialization()
    results['initialization'] = agent is not None
    
    # 测试 2: 市场分析
    results['market_analysis'] = test_market_analysis(agent)
    
    # 测试 3: 执行摘要
    results['executive_summary'] = test_executive_summary(agent)
    
    # 测试 4: 展望生成
    results['outlook'] = test_outlook_generation(agent)
    
    # 测试 5: 完整报告
    results['full_report'] = test_full_report(agent)
    
    # 总结
    print("\n" + "=" * 70)
    print("  测试总结")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n总计: {total} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {total - passed} 个")
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败/跳过"
        print(f"  - {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  部分测试失败，通过率: {passed/total*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("  测试完成")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

