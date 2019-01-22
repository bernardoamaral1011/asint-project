from math import sin, cos, sqrt, atan2, radians


def calc_distance(lat1_, lon1_, lat2_, lon2_, radius):
    # approximate radius of earth in km
    R = 6373.0
    # everything in km's
    lat1 = radians(float(lat1_))
    lon1 = radians(float(lon1_))
    lat2 = radians(float(lat2_))
    lon2 = radians(float(lon2_))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    try:
        float(radius)
    except ValueError:
        return False
        
    if distance <= float(radius):
        return True
    return False
    