
import enum



class SideType(enum.Enum):
    BUE = "buy"
    SELL = "sell"

class OrderType(enum.Enum):
    LIMIT = "limit"
    MARKET = "market"