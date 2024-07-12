#!/usr/bin/env python3

import sys
import statistics
import numpy as np

class Bot:
    def __init__(self):
        self.botState = BotState()

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            self.parse(reading)

    def parse(self, info: str):
        tmp = info.split(" ")
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        if tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
        if tmp[0] == "action":
            dollars = self.botState.stacks["USDT"]
            btc = self.botState.stacks["BTC"]
            closes = self.botState.charts["USDT_BTC"].closes
            current_closing_price = closes[-1]
            affordable = dollars / current_closing_price

            # Calculate moving averages
            short_ma = self.calculate_moving_average(closes, 10)  # Adjusted from 5 to 10
            long_ma = self.calculate_moving_average(closes, 30)  # Adjusted from 15 to 30

            # Calculate RSI and MACD
            rsi = self.calculate_rsi(closes, 20)  # Adjusted from 14 to 20
            macd_line = self.calculate_macd(closes, 15, 35)  # Adjusted from 12, 26 to 15, 35


            # Calculate signal line for MACD
            signal_line = self.calculate_ema(macd_line[-9:], 9)

            # Ensure macd_line and signal_line have the same shape
            min_length = min(len(macd_line), len(signal_line))
            macd_line = macd_line[-min_length:]
            signal_line = signal_line[-min_length:]


            if dollars > 500:
                # Use RSI, MACD, and moving average crossover for buying
                if short_ma > long_ma * 0.95 and rsi < 40 and sum(macd > signal for macd, signal in zip(macd_line, signal_line)) / min_length > 0.6:  # Adjusted RSI from 35 to 40
                    amount_to_buy = 0.5 * affordable
                    print(f'buy USDT_BTC {amount_to_buy}', flush=True)
                    self.botState.buy_price = current_closing_price
                    self.botState.trailing_stop_loss = current_closing_price * 0.95  # Set the initial trailing stop loss
                    self.botState.take_profit_level = current_closing_price * 1.10  # Set take profit level to 10% above buy price
                else:
                    print("no_moves", flush=True)
            else:
                # Update the trailing stop loss if the price has gone up
                if current_closing_price > self.botState.buy_price:
                    self.botState.trailing_stop_loss = max(self.botState.trailing_stop_loss, current_closing_price * 0.95)
                # Sell if the price has gone below the trailing stop loss or above the take profit level
                if current_closing_price < self.botState.trailing_stop_loss * 1.05 or current_closing_price > self.botState.take_profit_level * 0.95:
                    print(f'sell USDT_BTC {btc}', flush=True)
                    self.botState.buy_price = None
                    self.botState.trailing_stop_loss = None
                    self.botState.take_profit_level = None
                else:
                    print("no_moves", flush=True)


    def calculate_moving_average(self, prices, window):
        if len(prices) < window:
            return sum(prices) / len(prices)
        return sum(prices[-window:]) / window

    def calculate_rsi(self, prices, window):
        deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
        gains = [deltas[i] if deltas[i] > 0 else 0 for i in range(len(deltas))]
        losses = [-deltas[i] if deltas[i] < 0 else 0 for i in range(len(deltas))]
        avg_gain = sum(gains[-window:]) / window
        avg_loss = sum(losses[-window:]) / window
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, prices, short_window, long_window):
        short_ema = self.calculate_ema(prices, short_window)
        long_ema = self.calculate_ema(prices, long_window)
        macd_line = [short - long for short, long in zip(short_ema, long_ema)]
        return macd_line

    def calculate_ema(self, prices, window):
        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()
        ema = np.convolve(prices, weights, mode='full')[:len(prices)]
        if len(ema) > window:
            ema[:window] = ema[window]
        else:
            ema[:window] = ema[-1]
        return ema

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            if key == "date":
                self.date = int(value)
            if key == "high":
                self.high = float(value)
            if key == "low":
                self.low = float(value)
            if key == "open":
                self.open = float(value)
            if key == "close":
                self.close = float(value)
            if key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)

class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)

class BotState:
    def __init__(self):
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = dict()
        self.charts = dict()
        self.take_profit_level = 0
        self.buy_price = None
        self.trailing_stop_loss = None

    def update_chart(self, pair: str, new_candle_str: str):
        if not (pair in self.charts):
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        if key == "time_per_move":
            self.timePerMove = int(value)
        if key == "candle_interval":
            self.candleInterval = int(value)
        if key == "candle_format":
            self.candleFormat = value.split(",")
        if key == "candles_total":
            self.candlesTotal = int(value)
        if key == "candles_given":
            self.candlesGiven = int(value)
        if key == "initial_stack":
            self.initialStack = int(value)
        if key == "transaction_fee_percent":
            self.transactionFee = float(value)
        if key == "take_profit_level":
            self.take_profit_level = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))

if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
