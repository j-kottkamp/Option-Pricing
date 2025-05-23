import datetime

def calc_time_delta(strike):
    now = datetime.date.today()
    strikeDate = datetime.datetime.strptime(strike, "%d.%m.%Y").date()
    
    return (strikeDate - now).days