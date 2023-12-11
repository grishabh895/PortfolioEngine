from flask import Flask, request, render_template
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Mapping of stock symbols to company names
mapping = {
    'TSLA': 'Tesla, Inc.',
    'CAT': 'Caterpillar',
    'NEE': 'NextEra Energy, Inc.',
    'AMZN': 'Amazon.com, Inc.',
    'GOOGL': 'Alphabet Inc.',
    'CRM': 'Salesforce.com, Inc.',
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'PG': 'Procter & Gamble Company',
    'V': 'Visa Inc.',
    'JNJ': 'Johnson & Johnson',
    'WMT': 'Walmart Inc.',
    'BRK.B': 'Berkshire Hathaway Inc.',
    'KO': 'The Coca-Cola Company',
    'JPM': 'JPMorgan Chase & Co.',
    'MA': 'Mastercard',
    'BE': 'Bloom Energy Corporation',
    'PLUG': 'Plug Power Inc.',
    'NVDA': 'NVIDIA Corporation',
    'NFLX': 'Netflix, Inc.',
    'PYPL': 'PayPal Holdings, Inc.',
    'V': 'Visa Inc.',
    'BA': 'The Boeing Company',
    'CSCO': 'Cisco Systems, Inc.',
    'INTC': 'Intel Corporation',
    'ABBV': 'AbbVie Inc.',
    'MA': 'Mastercard Incorporated',
    'WMT': 'Walmart Inc.',
    'IBM': 'International Business Machines Corporation',
    'XOM': 'Exxon Mobil Corporation',
    'VOO': 'Vanguard 500 Index Fund ETF',
    'VTI': 'Vanguard Total Stock Market Index Fund ETF',
    'FNILX':'Fidelity ZERO Large Cap Index',
    'SPY': 'SPDR S&P 500 ETF Trust',
    'IVV': 'iShares Core S&P 500 ETF',
    'SWPPX': 'Schwab S&P 500 Index Fund',
    'ADBE': 'Adobe',
    'AMAT': 'Applied Materials',
    'WWD': 'Woodward'

}

all_stocks = {
    'Ethical Investing': ['MSFT', 'CAT', 'WWD', 'MA', 'ADBE', 'AMAT'],
    'Growth Investing': ['AMZN', 'GOOGL', 'CRM', 'NVDA', 'NFLX', 'PYPL'],
    'Index Investing': ['VOO', 'VTI', 'FNILX', 'SPY', 'IVV', 'SWPPX'],
    'Quality Investing': ['AAPL', 'PG', 'JNJ', 'INTC', 'ABBV', 'MA'],
    'Value Investing': ['BRK.B', 'KO', 'JPM', 'WMT', 'IBM', 'XOM']
}

def get_historical_data(symbol):
    base_url = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
    from_date = (datetime.today() - timedelta(days=8)).strftime('%Y-%m-%d')
    to_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    date_filter = '?from={}&to={}'.format(from_date, to_date)

    response = requests.get(base_url + symbol + date_filter + " &apikey=teWiXQJYRwrOQgcE51x2wNeIVWDpB12o")

    if response.status_code == 200:
        data = response.json()
        return data.get('historical', [])[:5]
    else:
        return []

def suggest_top_stocks(strategy, all_stocks):
    top_stocks = []

    
    for symbol in all_stocks.get(strategy, []):
        historical_data = get_historical_data(symbol)
        growth_rate = get_growth_rate(historical_data)
        print(symbol)
        print(growth_rate)
        stock_info = {
            'symbol': symbol,
            'company_name': mapping.get(symbol, 'N/A'),
            'growth_rate': growth_rate
        }

        top_stocks.append(stock_info)

    # Sort stocks based on growth rate in descending order
    top_stocks = sorted(top_stocks, key=lambda x: x['growth_rate'], reverse=True)

    # Get the top 3 stocks
    top_3_stocks = top_stocks[:3]

    return top_3_stocks

def get_growth_rate(data):
    if data:
        closing_prices = [entry['close'] for entry in data]
        growth_rate = (closing_prices[0] - closing_prices[-1]) / closing_prices[-1] * 100
        return growth_rate
    else:
        return 0

def suggest_stocks(strategies):
    selected_stocks = []

    for strategy in strategies:
        if strategy in all_stocks:
            top_stocks = suggest_top_stocks(strategy, all_stocks)
            selected_stocks.extend([stock['symbol'] for stock in top_stocks])

    return selected_stocks

def calculate_allocation(invest_amount, selected_stocks):
    allocation_per_stock = invest_amount / len(selected_stocks)
    return allocation_per_stock

def calculate_portfolio_value(selected_stocks, allocation_per_stock):
    portfolio_value = 0
    portfolio_composition = []

    for symbol in selected_stocks:
        historical_data = get_historical_data(symbol)
        # Ensure there are at least 5 days of historical data
        if len(historical_data) >= 5:
            # Calculate growth rate over the last 5 days
            growth_rate_5_days = get_growth_rate(historical_data[-5:])
        else:
            growth_rate_5_days = 0
        current_price = historical_data[0]['close'] if historical_data else 0
        shares_to_buy = int(allocation_per_stock / current_price)
        portfolio_value += shares_to_buy * current_price
        company_name = mapping.get(symbol, 'N/A')

        result = {entry['date']: entry['close'] for entry in historical_data}

        # Convert Timestamp keys to strings
        result_str_keys = {key: value for key, value in result.items()}

        # Add detailed information to the portfolio_composition list
        composition_item = {
            "symbol": symbol,
            "company_name": company_name,
            "current_price": current_price,
            "shares_to_buy": shares_to_buy,
            "result": result_str_keys,
            "strategies": [strategy for strategy, stocks in all_stocks.items() if symbol in stocks],
            "growth_rate_5_days" : growth_rate_5_days
        }
        portfolio_composition.append(composition_item)

    return portfolio_value, portfolio_composition

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('index.html', strategies=['Ethical Investing', 'Growth Investing', 'Index Investing', 'Quality Investing', 'Value Investing'])
    elif request.method == 'POST':
        invest_amount_str = request.form.get('invest_amount')

        # Validate if investment amount is a valid number
        try:
            invest_amount = float(invest_amount_str)
        except ValueError:
            tempData = {"error": "Investment amount should be a valid number."}
            return render_template('index.html', strategies=['Ethical Investing', 'Growth Investing', 'Index Investing', 'Quality Investing', 'Value Investing'], **tempData)
        
        selected_strategies = request.form.getlist('strategy')

        if invest_amount < 5000:
            tempData = {"error": "Minimum investment amount is $5000."}
            return render_template('index.html', **tempData)
        
        if len(selected_strategies) > 2:
            tempData = {"error": "Please select up to two strategies."}
            return render_template('index.html', strategies=['Ethical Investing', 'Growth Investing', 'Index Investing', 'Quality Investing', 'Value Investing'], **tempData)

        selected_stocks = suggest_stocks(selected_strategies)

        if not selected_stocks:
            tempData = {"error": "Please select at least one strategy"}
            return render_template('index.html', **tempData)

        allocation_per_stock = calculate_allocation(invest_amount, selected_stocks)
        portfolio_value, portfolio_composition = calculate_portfolio_value(selected_stocks, allocation_per_stock)

        tempData = {
            "selected_stocks": selected_stocks,
            "allocation_per_stock": allocation_per_stock,
            "portfolio_composition": portfolio_composition,
            "portfolio_value": portfolio_value,
            "error": "success"
        }

        return render_template('index.html', strategies=['Ethical Investing', 'Growth Investing', 'Index Investing', 'Quality Investing', 'Value Investing'], **tempData)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
