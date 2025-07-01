import requests
import json
import os
import asyncio
from gql import Client, gql
import config

BITQUERY_REST_URL = "https://streaming.bitquery.io/graphql"
BITQUERY_TOKEN = config.BITQUERY_TOKEN
wallet_address = config.WALLET_ADDRESS

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BITQUERY_TOKEN}"
}

### ----------- REST API Queries ----------- ###

def run_bitquery(query: str, variables: dict = {}):
    payload = json.dumps({
        "query": query,
        "variables": json.dumps(variables)
    })
    response = requests.post(BITQUERY_REST_URL, headers=HEADERS, data=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status {response.status_code}: {response.text}")

# 1. Get Top Trending Four Meme Tokens
def get_trending_tokens():
    query = """
      query TrendingTokens {
        EVM(network: bsc, dataset: realtime) {
          DEXTradeByTokens(
            limit: {count: 10}
            where: {
              Trade: {
                Currency: {SmartContract: {not: "0x"}}
                Dex: {ProtocolName: {is: "fourmeme_v1"}},
                Success: true
              }
            }
            orderBy: {descendingByField: "uniq_traders"}
          ){
            Trade{
              Currency{
                Name
                Symbol
                SmartContract
              }
            }
            uniq_traders: uniq(of: Transaction_From)
          }
        }
      }
    """
    return run_bitquery(query)

# 2. Get Token Volatility
def get_token_volatility(buy_mint: str, sell_mint: str):
    query = """
    query Volatility {
      EVM(dataset: realtime, network: bsc) {
        DEXTrades(
          where: {
            Trade: {
              Buy: { Currency: { SmartContract: { is: "%s" } } }
              Sell: { Currency: { SmartContract: { is: "%s" } } }
            }
          }
        ) {
          volatility: standard_deviation(of: Trade_Buy_PriceInUSD)
        }
      }
    }
    """ % (buy_mint, sell_mint)
    return run_bitquery(query)

# 3. Get Trade metrics like Volume and Trades Count
def get_trade_metrics(mint_address: str):
    query = """
      query TradeMetrics {
        EVM(network: bsc, dataset: realtime) {
          DEXTradeByTokens(
            where: {
              Trade: {
                Currency: {
                  SmartContract: {
                    is: "%s"
                  }
                }
              }
            }
          ){
            volume: sum(of:Trade_Side_AmountInUSD)
            trades: count
          }
        }
      }
    """ % (mint_address)
    return run_bitquery(query)

# 5. Get Wallet Balances
def get_wallet_balances(wallet_address: str):
    query = """
    query WalletBalances {
      EVM(network: bsc, dataset: combined) {
        BalanceUpdates(
          where: {BalanceUpdate: {Address: {is: "%s"}}}
          orderBy: {descendingByField: "balance"}
        ) {
          Currency {
            Name
            Symbol
            SmartContract
          }
          balance:sum(of: BalanceUpdate_Amount, selectWhere: {ne: "0"})
        }
      }
    }
    """ % (wallet_address)
    return run_bitquery(query)