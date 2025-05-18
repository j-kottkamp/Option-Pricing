import datetime

def calcTimeDelta(strike):
    now = datetime.date.today()
    strikeDate = datetime.datetime.strptime(strike, "%d.%m.%Y").date()
    
    return (strikeDate - now).days