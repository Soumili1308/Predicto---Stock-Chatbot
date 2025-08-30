from flask import Flask, jsonify, request, render_template
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

# Excel file path
EXCEL_FILE = 'stock_data.xlsx'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/live')
def live():
    return render_template('live.html')

@app.route('/api/predict/<symbol>')
def predict_stock(symbol):
    symbol = symbol.upper()

    # Validate symbol
    supported_symbols = ['AAPL', 'GOOG', 'TSLA']
    if symbol not in supported_symbols:
        return jsonify({"error": "Symbol not supported"}), 400

    try:
        # Load the appropriate sheet from the Excel file
        df = pd.read_excel(EXCEL_FILE, sheet_name=symbol)
        df.columns = df.columns.str.strip()

        # Required columns
        required_cols = ['date', 'price', 'high', 'low', 'vol', '%change']
        if not all(col in df.columns for col in required_cols):
            return jsonify({"error": f"Missing required columns. Found columns: {df.columns.tolist()}"}), 400

        # Clean the data
        df[required_cols[1:]] = df[required_cols[1:]].apply(pd.to_numeric, errors='coerce')
        df.dropna(inplace=True)
        df = df.sort_values('date')

        # Train-test split (80-20)
        train_size = int(len(df) * 0.8)
        train_data = df.iloc[:train_size]
        test_data = df.iloc[train_size:]

        # Train model
        model = RandomForestRegressor()
        X_train = train_data[['high', 'low', 'vol', '%change']]
        y_train = train_data['price']
        model.fit(X_train, y_train)

        # Predict
        X_test = test_data[['high', 'low', 'vol', '%change']]
        y_test = test_data['price']
        predictions = model.predict(X_test)

        last_pred = predictions[-1]
        last_actual = y_test.iloc[-1]
        signal = "Buy" if last_pred > last_actual else "Sell"

        return jsonify({
    "last_20_day_prediction": {
        "predicted": round(float(last_pred), 2),
        "actual": round(float(last_actual), 2),
        "signal": signal
    }
})

    except Exception as e:
        return jsonify({"error": f"Failed to load Excel data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
