import asyncio
import time
import config

from bitquery_utils import (
    get_trending_tokens,
    get_token_volatility,
    get_wallet_balances,
    get_trade_metrics
)
from ai_decision import analyze_token_and_decide

WALLET_ADDRESS = config.WALLET_ADDRESS
BASE_TOKEN_MINT = "0x"

### ----------- AI Trading Loop ----------- ###

def ai_trading_loop():
    print("Starting AI Trading Loop...")

    while True:
        try:
            print("\nFetching trending tokens...")
            trending = get_trending_tokens()
            tokens = trending.get("data", {}).get("EVM", {}).get("DEXTradeByTokens", [])
            
            if not tokens:
                print("No trending tokens found.")
                time.sleep(30)
                continue

            print("Fetching wallet balances...")
            wallet_data = get_wallet_balances(WALLET_ADDRESS)
            balances = wallet_data.get("data", {}).get("EVM", {}).get("BalanceUpdates", [])

            owned_tokens_mint_addresses = set()
            for balance in balances:
                currency = balance.get("BalanceUpdate", {}).get("Currency", {})
                mint_address = currency.get("SmartContract")
                if mint_address:
                    owned_tokens_mint_addresses.add(mint_address)

            for token in tokens:
                currency = token["Trade"]["Currency"]
                mint = currency["SmartContract"]
                symbol = currency["Symbol"]
                name = currency["Name"]
                uniq_traders = token["uniq_traders"]

                print(f"\nAnalyzing token: {symbol} ({name})")

                # Fetch additional token data
                trade_data = get_trade_metrics(mint)
                trade_metrics = trade_data.get("data", {}).get("EVM", {}).get("DEXTradeByTokens", [])
                if trade_metrics:
                    volume = trade_metrics[0].get("volume", "Unknown")
                    trades = trade_metrics[0].get("trades", "Unknown")
                else:
                    volume = "Unknown"
                    trades = "unknown"

                volatility_data = get_token_volatility(mint, BASE_TOKEN_MINT)
                dex_trades = volatility_data.get("data", {}).get("EVM", {}).get("DEXTrades", [])
                if dex_trades:
                    volatility = dex_trades[0].get("volatility", "Unknown")
                else:
                    volatility = "Unknown"

                wallet_holds_token = mint in owned_tokens_mint_addresses

                # AI Decision Making
                token_data = {
                    "name": name,
                    "symbol": symbol,
                    "mint_address": mint,
                    "volume": volume,
                    "trades": trades,
                    "volatility": volatility,
                    "uniq_traders": uniq_traders,
                    "wallet_holds_token": wallet_holds_token
                }

                decision = analyze_token_and_decide(token_data)
                print(f"AI Decision for {symbol}: {decision}")

                # Placeholder for trade execution logic
                if decision == "Buy":
                    if wallet_holds_token:
                        print(f"Already holding {symbol}, considering HOLD or additional BUY logic.")
                    else:
                        print(f"Would execute BUY for {symbol}")
                elif decision == "Sell":
                    if wallet_holds_token:
                        print(f"Would execute SELL for {symbol}")
                    else:
                        print(f"Cannot SELL {symbol}, wallet doesn't hold it.")
                elif decision == "Hold":
                    if wallet_holds_token:
                        print(f"Holding {symbol}.")
                    else:
                        print(f"Cannot HOLD {symbol}, wallet doesn't hold it.")
                elif decision == "Avoid":
                    print(f"Skipping {symbol} due to risk factors.")
                else:
                    print(f"Holding off on {symbol} for now.")

            time.sleep(60)  # Wait before re-evaluating

        except Exception as e:
            print(f"Error in trading loop: {e}")
            time.sleep(30)


### ----------- Entry Point ----------- ###

if __name__ == "__main__":
    try:
        ai_trading_loop()

    except KeyboardInterrupt:
        print("Shutting down Trading Agent...")
