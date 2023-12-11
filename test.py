import requests
from datetime import datetime, timedelta
# Function to make API call to Financial Modeling Prep to get company data
def get_company_data(symbol):
    base_url = 'https://financialmodelingprep.com/api/v3/historical-price-full/'
    from_date = (datetime.today() - timedelta(days=8)).strftime('%Y-%m-%d')
    to_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    date_filter = '?from={}&to={}'.format(from_date, to_date)

    response = requests.get(base_url + symbol + date_filter + " &apikey=JOXgbXhnH1s4mGaTdRFjWSToeQAEBdLl")
    
    if response.status_code == 200:
        return response.json()  # Assuming the API returns a list, take the first item
    else:
        print(f"Failed to fetch data for {symbol}")
        return None

# Function to calculate intrinsic value for each company
def calculate_intrinsic_value(companies):
    for company in companies:
        symbol = company['symbol']
        company_data = get_company_data(symbol)

        if company_data:
            # Assuming earnings per share (EPS) is available for the company
            eps = float(company_data.get('eps', 0))
            print('eps')
            print(eps)
            # Assuming a target P/E ratio for valuation
            target_pe_ratio = 15  # You may adjust this based on your strategy

            # Calculate intrinsic value using the P/E ratio
            intrinsic_value = eps * target_pe_ratio

            # Store the calculated intrinsic value in the company's data structure
            company['intrinsic_value'] = intrinsic_value

# Example usage:
companies = [
    {'name': 'CompanyA', 'symbol': 'AAPL'},
    {'name': 'CompanyB', 'symbol': 'MSFT'},
    # Add more companies with relevant data
]

calculate_intrinsic_value(companies)

# Print the calculated intrinsic values
for company in companies:
    print(f"{company['name']} - Intrinsic Value: ${company.get('intrinsic_value', 0):.2f}")
