def is_leap(year):
    leap = False
    notleap = True
    if year % 100 == 0 and year % 400 == 0:
        return notleap
    elif year % 100 == 0:
        return leap
    elif year % 4 == 0:
        return notleap
    return leap
