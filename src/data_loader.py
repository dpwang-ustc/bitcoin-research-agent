import pandas as pd
import yfinance as yf
from datetime import datetime
import time

def load_bitcoin_data(start='2018-01-01', end=None):
    if end is None:
        end = datetime.today().strftime('%Y-%m-%d')
    
    # 尝试多次下载，添加重试逻辑
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f'Downloading BTC-USD data (attempt {attempt + 1}/{max_retries})...')
            # 添加更多参数来确保下载成功
            data = yf.download('BTC-USD', start=start, end=end, progress=False, auto_adjust=True)
            
            if data.empty:
                print(f'Warning: Downloaded data is empty on attempt {attempt + 1}')
                if attempt < max_retries - 1:
                    print('Retrying in 2 seconds...')
                    time.sleep(2)
                    continue
                else:
                    raise ValueError('Failed to download BTC-USD data after all retries')
            
            # 重置列名，移除多级索引
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            data.to_csv('data/raw/bitcoin_price.csv', index=True)
            print(f'Successfully downloaded {len(data)} rows to data/raw/bitcoin_price.csv')
            return data
            
        except Exception as e:
            print(f'Error on attempt {attempt + 1}: {str(e)}')
            if attempt < max_retries - 1:
                print('Retrying in 2 seconds...')
                time.sleep(2)
            else:
                print('All retries failed. Please check your internet connection or try again later.')
                raise

if __name__ == '__main__':
    df = load_bitcoin_data()
    print(df.tail())
