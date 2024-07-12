# The Candle class represents a single candlestick in a candlestick chart.
class Candle:
    def __init__(self, format, intel):
        # Split the input into a list of strings
        tmp = intel.split(",")
        # For each string in the list, assign it to the corresponding attribute of the candle
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
        # Return a string representation of the candle
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)