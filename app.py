from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import requests

# Initialize app
app = Flask(__name__)
CORS(app)

def fetch_stock_info(symbol, exchange='NSE'):
    """Fetch current market price and company name from NSE or BSE."""
    if exchange.upper() == 'NSE':
        ticker = f'{symbol}.NS'
    elif exchange.upper() == 'BSE':
        ticker = f'{symbol}.BO'
    else:
        return None

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Fetch price and company name
        price = info.get('regularMarketPrice')
        company_name = info.get('longName')

        if not price or not company_name:
            return None

        return {
            'symbol': symbol,
            'exchange': exchange,
            'company_name': company_name,
            'price': price
        }
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/stock', methods=['GET'])
def get_stock_info():
    """API Endpoint to get current stock price and company name."""
    symbol = request.args.get('symbol')
    exchange = request.args.get('exchange', 'NSE')  # Default to NSE

    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400

    stock_info = fetch_stock_info(symbol, exchange)

    if stock_info is None:
        return jsonify({"error": "Invalid symbol or no data found"}), 404

    return jsonify(stock_info)


  # Fetch price and Mutual fund Scheme and NAV 
@app.route('/nav/<scheme_code>', methods=['GET'])
def get_mf_nav(scheme_code):
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data and "data" in data and len(data["data"]) > 0:
            result = {
                "nav": float(data["data"][0]["nav"]),
                "date": data["data"][0]["date"],
                "scheme_name": data["meta"]["scheme_name"]
            }
            return jsonify(result)
        return jsonify({"error": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
