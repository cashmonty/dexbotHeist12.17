import pandas as pd
import requests

# Constants

solanafmBaseUrl = "https://api.solana.fm"
epochFromTimestamp = "1703538136"
epochToTimestamp = "1704142936"
# Define your CSV file path
wallets_csv_path = 'table.csv'

# Read wallet addresses from the 'Text1' column of the CSV
wallet_addresses = pd.read_csv(wallets_csv_path)['Text1'].tolist()
# Initialize DataFrame
df = pd.DataFrame(columns=[
    "wallet_address", "transactionHash", "action", "amount", "timestamp"
])

# Function to fetch and process transactions
def fetch_transactions(walletAddress):
    page = 1
    while True:
        response = requests.get(f"{solanafmBaseUrl}/v0/accounts/{walletAddress}/transfers",
                                params={
                                    "utcFrom": epochFromTimestamp,
                                    "utcTo": epochToTimestamp,
                                    "page": page,
                                },
                                headers={"ApiKey": apikey})
        data = response.json()
        totalPages = data['pagination']['totalPages']

        for transaction in data['results']:
            for movement in transaction['data']:
                if movement['action'] in ['swap', 'mint']:
                    df.loc[len(df)] = [
                        walletAddress,
                        transaction['transactionHash'],
                        movement['action'],
                        movement['amount'],
                        movement['timestamp']
                    ]
        page += 1
        if page > totalPages:
            break

# Process each wallet
for wallet in wallet_addresses:
    fetch_transactions(wallet)

# Display the DataFrame
print(df)
