from .bellmannx import calculate_profit_ratio_for_path, bellman_ford
from .utils import load_exchange_graph
import ccxt.async as ccxt
import asyncio
import json
import time
# This script writes the profit ratio for arbitrage available and response time for each US exchange into
# exchange_profits.csv


us_exchanges = []
for exchange_name in ccxt.exchanges:
    exchange = getattr(ccxt, exchange_name)()
    if 'US' in exchange.countries:
        us_exchanges.append(exchange)

exchange_graphs = {}


def refresh_graphs():

    async def add_to_graph(name):
        start_time = time.time()
        graph = load_exchange_graph(name, fees=True)
        end_time = time.time() - start_time
        exchange_graphs[name] = {'graph': graph, 'time': end_time}

    futures = [add_to_graph(name) for name in us_exchanges]
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*futures))


data = {}

for i in range(2160):
    refresh_graphs()

    # data gathered on this iteration
    iteration_data = {}

    for key, value in exchange_graphs.items():
        paths = bellman_ford(value['graph'], 'BTC', unique_paths=True, loop_from_source=False)

        ratio = -1
        for path in paths:
            r = calculate_profit_ratio_for_path(value['graph'], path)
            if r > ratio:
                ratio = r

        data[i][key] = {'ratio': ratio, 'time': value['time']}

    time.sleep(10)


with open('data.json', 'w') as outfile:
    json.dump(data, outfile)
