import json
from datetime import datetime, timedelta
import requests


class CurrencyExchange:
    def __init__(self, max_days=10):
        self.max_days = max_days

    async def execute(self, server, ws, days, currencies):
        days = min(days, self.max_days)

        results = await self.get_currency_rates(days, currencies)
        parsed_results = self.parse_results(results, currencies)
        await server.send_to_clients(f"Currency exchange rates: {json.dumps(parsed_results)}")

    def parse_results(self, results, currencies):
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

    async def get_currency_rates(self, days, currencies):
        results = []
        for i in range(min(days, self.max_days)):
            today = datetime.today() - timedelta(days=i)
            date = today.strftime('%d.%m.%Y')
            url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
            response = requests.get(url)

            if response.status_code == 200:
                results.append(response.json())
            else:
                raise Exception(f"Failed to fetch exchange rates. Status code: {response.status_code}")

        return results
