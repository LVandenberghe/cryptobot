from trade import BotState
import sys

# The Bot class is the main class that runs the trading bot.
class Bot:
    def __init__(self):
        # Initialize the bot state
        self.botState = BotState()

    def run(self):
        # Main loop that keeps the bot running
        while True:
            # Read input from the standard input
            reading = input()
            # If the input is empty, continue to the next iteration
            if len(reading) == 0:
                continue
            # Parse the input
            self.parse(reading)

    def parse(self, info: str):
        # Split the input into a list of strings
        tmp = info.split(" ")
        # If the first string is "settings", update the bot settings
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        # If the first string is "update", update the game state
        if tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
        # If the first string is "action", perform an action
        if tmp[0] == "action":
            # Get the current amount of dollars and BTC
            dollars = self.botState.stacks["USDT"]
            btc = self.botState.stacks["BTC"]
            # Get the closing prices of the BTC/USDT pair
            closes = self.botState.charts["USDT_BTC"].closes
            # Get the current closing price
            current_closing_price = closes[-1]
            # Calculate how much BTC can be bought with the current amount of dollars
            affordable = dollars / current_closing_price
            # Print the current state of the bot to the standard error
            print(f'My stacks are {dollars}. The current closing price is {current_closing_price}. So I can afford {affordable}', file=sys.stderr)
            # If the bot has less than 100 dollars, do nothing
            if dollars < 100:
                print("no_moves", flush=True)
            else:
                # Calculate the average closing price of the last 5 candles
                avg_closing_price = sum(closes[-5:]) / 5
                # If the current closing price is higher than the average, sell BTC
                if current_closing_price > avg_closing_price or btc > 0.5:
                    # Calculate the amount of BTC to sell
                    sell_amount = min(0.5 * affordable, btc)
                    # If the sell amount is greater than 0, sell BTC
                    if sell_amount > 0:
                        print(f'sell USDT_BTC {sell_amount}', flush=True)
                    else:
                        print("no_moves", flush=True)
                else:
                    # If the current closing price is less than the average minus a stop loss level, buy BTC
                    stop_loss_level = 0.05  # 5% stop loss level
                    if current_closing_price < avg_closing_price * (1 - stop_loss_level):
                        print(f'buy USDT_BTC {0.5 * affordable}', flush=True)
                    else:
                        print("no_moves", flush=True)
