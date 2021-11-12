def human_readable_stat(c):
    """
    Transform a timedelta expressed in seconds into a human readable string

    Parameters
    ----------
    c
        Timedelta expressed in seconds

    Returns
    ----------
    string
        Human readable string
    """
    c = int(float(c))
    # years = c // 31104000
    # months = c // 2592000
    days = c // 86400
    hours = c // 3600 % 24
    minutes = c // 60 % 60
    seconds = c % 60
    # if years > 0:
    #     return str(years) + "Y " + str(months) + "MO " + str(days) + "D " + str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
    # if months > 0:
    #     return str(months) + "MO " + str(days) + "D " + str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
    if days > 0:
        return str(days) + "D " + str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
    if hours > 0:
        return str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
    if minutes > 0:
        return str(minutes) + "m " + str(seconds) + "s"
    return str(seconds) + "s"
