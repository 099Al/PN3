
import enum
from sqlalchemy import Enum


class SideType(enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(enum.Enum):
    LIMIT = "limit"
    MARKET = "market"

class ActivityType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DONE = "DONE"
    CANCELED = "CANCELED"

class OrderStatusType(enum.Enum):
    NEW = "NEW"
    CANCELED = "CANCELED"
    DONE = "DONE"
    REJECTED = "REJECTED"

def pg_enum(enum_cls, name):
    return Enum(enum_cls, name=name, values_callable=lambda x: [e.value for e in x], create_type=False)

SideTypeEnum = pg_enum(SideType, "sidetype")
OrderTypeEnum = pg_enum(OrderType, "ordertype")
ActivityTypeEnum = pg_enum(ActivityType, "activitytype")
OrderStatusTypeEnum = pg_enum(OrderStatusType, "orderstatus")