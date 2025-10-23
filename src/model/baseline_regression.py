import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def train_regression_model():
    df = pd.read_csv('data/processed/bitcoin_features.csv')
    X = df[['MA7', 'MA30', 'Volatility']]
    y = df['Close']
    model = LinearRegression().fit(X, y)
    preds = model.predict(X)
    mse = mean_squared_error(y, preds)
    print(f'Model trained. MSE: {mse:.2f}')
    return model

if __name__ == '__main__':
    model = train_regression_model()
