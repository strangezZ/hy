import decimal
import datetime


def alchemy_encoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        # return obj.isoformat()
        return str(obj)
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
