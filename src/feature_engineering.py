import pandas as pd
import numpy as np

def add_features(df):
    # 确保数值列是数字类型
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['Return'] = df['Close'].pct_change(fill_method=None)
    df['MA7'] = df['Close'].rolling(window=7).mean()
    df['MA30'] = df['Close'].rolling(window=30).mean()
    df['Volatility'] = df['Return'].rolling(window=7).std()
    df.dropna(inplace=True)
    df.to_csv('data/processed/bitcoin_features.csv', index=True)
    print('Processed features saved to data/processed/bitcoin_features.csv')
    return df

if __name__ == '__main__':
    df = pd.read_csv('data/raw/bitcoin_price.csv', index_col=0, parse_dates=True)
    print(f'Loaded {len(df)} rows from bitcoin_price.csv')
    df = add_features(df)
    print(f'Generated {len(df)} rows with features')
