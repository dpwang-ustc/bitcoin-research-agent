import pandas as pd

class AgentReasoner:
    def __init__(self, model=None):
        self.model = model

    def analyze_trend(self, df):
        trend = 'uptrend' if df['Return'].mean() > 0 else 'downtrend'
        print(f'Agent detected a {trend} in the recent period.')
        return trend

if __name__ == '__main__':
    df = pd.read_csv('data/processed/bitcoin_features.csv')
    agent = AgentReasoner()
    agent.analyze_trend(df)
