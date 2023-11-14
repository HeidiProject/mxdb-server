from datetime import datetime
from bson import ObjectId

def json_serialhelper(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    if isinstance(obj, ObjectId):
        serial = str(obj)
        return serial
    raise TypeError ("Type not serializable")
