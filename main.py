import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
import argparse


async def fetch_currency_rate(date, currencies):
    async with aiohttp.ClientSession() as session:
        url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
        async with session.get(url) as response:
            data = await response.json()
            return data


async def get_currency_rates(days, currencies):
    today = datetime.today()
    date_list = [(today - timedelta(days=i)).strftime('%d.%m.%Y') for i in range(days)]

    tasks = [fetch_currency_rate(date, currencies) for date in date_list]
    results = await asyncio.gather(*tasks)

    return results

def parse_results(results, currencies):
    parsed_results = []
    for result, date in zip(results, [datetime.today() - timedelta(days=i) for i in range(len(results))]):
        formatted_date = date.strftime('%d.%m.%Y')
        currency_info = result.get('exchangeRate', [])
        currency_data = {}

        for currency in currency_info:
            if currency['currency'] in currencies:
                currency_data[currency['currency']] = {
                    'sale': currency['saleRate'],
                    'purchase': currency['purchaseRate']
                }

        parsed_results.append({formatted_date: currency_data})

    return parsed_results

def main():
    parser = argparse.ArgumentParser(description='Get currency rates for the last N days.')
    parser.add_argument('days', type=int, help='Number of days to fetch currency rates')
    parser.add_argument('--currencies', nargs='+', default=['USD', 'EUR'], help='List of currencies to include in the results')
    args = parser.parse_args()

    if args.days > 10:
        print("Error: Number of days should not exceed 10.")
        return

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(get_currency_rates(args.days, args.currencies))
    parsed_results = parse_results(results, args.currencies)

    print(json.dumps(parsed_results, indent=2))

if __name__ == '__main__':
    main()
