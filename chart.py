from candle import Candle

# The Chart class represents a candlestick chart.
class Chart:
    def __init__(self):
        # Initialize the lists that store the dates, opening prices, highest prices, lowest prices, closing prices, and volumes of the candles
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        # Add a new candle to the chart
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)
