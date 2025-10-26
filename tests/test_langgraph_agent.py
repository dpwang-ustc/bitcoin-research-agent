"""
测试 LangGraph Agent

测试：
1. Agent 初始化
2. 简单查询
3. 完整工作流（可选，需要 API Key）
"""

import sys
import os
import io

# Force UTF-8 output for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_import():
    """测试 1: 导入模块"""
    print("\n" + "="*70)
    print("测试 1: 导入 LangGraph Agent 模块")
    print("="*70)
    
    try:
        from src.agent import BitcoinResearchAgent, ResearchState
        print("✅ 模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def test_agent_init():
    """测试 2: Agent 初始化"""
    print("\n" + "="*70)
    print("测试 2: 初始化 Agent（需要 API Key）")
    print("="*70)
    
    # 检查 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  未找到 OPENAI_API_KEY，跳过此测试")
        print("提示: export OPENAI_API_KEY='sk-...'")
        return False
    
    try:
        from src.agent import BitcoinResearchAgent
        
        agent = BitcoinResearchAgent(
            llm_provider="openai",
            llm_model="gpt-4o-mini",
            verbose=True
        )
        
        print("✅ Agent 初始化成功")
        return agent
        
    except Exception as e:
        print(f"❌ Agent 初始化失败: {e}")
        return None


def test_quick_query(agent):
    """测试 3: 快速查询（需要 Agent 和 API Key）"""
    print("\n" + "="*70)
    print("测试 3: 快速查询")
    print("="*70)
    
    if not agent:
        print("⚠️  Agent 未初始化，跳过此测试")
        return False
    
    try:
        print("\n提问: 什么是比特币？")
        print("-"*70)
        
        response = agent.chat("简单介绍一下比特币是什么")
        
        print(f"\nAgent 回复:\n{response}")
        print("\n✅ 快速查询测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 快速查询失败: {e}")
        return False


def test_workflow_structure():
    """测试 4: 工作流结构检查"""
    print("\n" + "="*70)
    print("测试 4: 检查工作流结构")
    print("="*70)
    
    try:
        from src.agent import BitcoinResearchAgent
        import inspect
        
        # 检查关键方法
        methods = [
            '_node_route_task',
            '_node_collect_data',
            '_node_process_data',
            '_node_analyze_regime',
            '_node_analyze_volatility',
            '_node_analyze_sentiment',
            '_node_analyze_capital',
            '_node_generate_insights',
            '_node_generate_report',
            '_node_quick_response',
            '_build_workflow',
            'run',
            'chat'
        ]
        
        missing_methods = []
        for method in methods:
            if not hasattr(BitcoinResearchAgent, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ 缺少方法: {', '.join(missing_methods)}")
            return False
        else:
            print(f"✅ 所有 {len(methods)} 个关键方法都存在")
            print("\n工作流节点:")
            for method in methods:
                if method.startswith('_node_'):
                    print(f"  - {method}")
            return True
        
    except Exception as e:
        print(f"❌ 工作流结构检查失败: {e}")
        return False


def test_full_analysis(agent):
    """测试 5: 完整分析流程（可选）"""
    print("\n" + "="*70)
    print("测试 5: 完整分析流程（较慢，约 2-3 分钟）")
    print("="*70)
    
    if not agent:
        print("⚠️  Agent 未初始化，跳过此测试")
        return False
    
    # 询问用户是否要运行完整测试
    print("\n⚠️  完整分析需要：")
    print("  1. 下载市场数据（~2000 行）")
    print("  2. 运行所有分析模块")
    print("  3. 调用 AI 生成洞察")
    print("  4. 生成完整报告")
    print("  总时间: 约 2-3 分钟")
    print("  成本: 约 ¥0.10-0.15 (gpt-4o-mini)")
    
    user_input = input("\n是否运行完整测试？(y/N): ").strip().lower()
    
    if user_input != 'y':
        print("⚠️  跳过完整分析测试")
        return False
    
    try:
        print("\n开始完整分析...")
        print("-"*70)
        
        result = agent.run("生成本周比特币市场完整分析报告")
        
        print("\n" + "="*70)
        print("分析结果:")
        print("="*70)
        
        # 检查结果
        if result.get('error'):
            print(f"❌ 分析失败: {result['error']}")
            return False
        
        # 显示关键信息
        print(f"\n✅ 任务类型: {result.get('task_type', 'N/A')}")
        print(f"✅ 最终步骤: {result.get('current_step', 'N/A')}")
        print(f"✅ 执行步骤数: {len(result.get('messages', []))}")
        
        # 显示报告预览
        if result.get('report'):
            report = result['report']
            print(f"\n📊 报告预览 (前 500 字符):")
            print("-"*70)
            print(report[:500])
            print("\n[...完整报告已生成...]")
        
        # 显示 AI 洞察
        if result.get('ai_insights'):
            insights = result['ai_insights']
            print(f"\n🧠 AI 洞察预览 (前 300 字符):")
            print("-"*70)
            print(insights[:300])
            print("\n[...完整洞察已生成...]")
        
        print("\n✅ 完整分析测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 完整分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("  LangGraph Agent 测试套件")
    print("="*70)
    
    results = {}
    
    # 测试 1: 导入
    results['import'] = test_import()
    
    # 测试 2: 初始化
    agent = test_agent_init()
    results['init'] = (agent is not None)
    
    # 测试 3: 快速查询
    if agent:
        results['quick_query'] = test_quick_query(agent)
    else:
        results['quick_query'] = False
    
    # 测试 4: 工作流结构
    results['workflow'] = test_workflow_structure()
    
    # 测试 5: 完整分析（可选）
    if agent:
        results['full_analysis'] = test_full_analysis(agent)
    else:
        results['full_analysis'] = False
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20s}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n总计: {passed_count}/{total_count} 测试通过")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！")
    elif passed_count >= 3:
        print("\n✅ 核心功能正常（部分测试跳过）")
    else:
        print("\n⚠️  存在失败的测试")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()

