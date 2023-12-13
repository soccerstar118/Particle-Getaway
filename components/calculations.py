import math


def dist_line_point(x1, y1, x2, y2, x3, y3) -> float:
    """x3,y3 is the point, x1 and x2 are the points making up the line"""
    px = x2 - x1
    py = y2 - y1

    norm = px * px + py * py

    u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    distance = (dx * dx + dy * dy) ** .5

    return distance


def within_bounds(small, number_put_in_bounds, large) -> float:
    if small <= number_put_in_bounds <= large:
        return number_put_in_bounds
    elif number_put_in_bounds > large:
        return large
    elif number_put_in_bounds < small:
        return small
    raise  # this code line should never be able to run


def col_mult(arr, mult, *, max_=float('inf')):
    temp_arr = [num * mult for num in arr]
    for i in range(len(temp_arr)):
        if max_ < temp_arr[i]:
            temp_arr[i] = max_
    return temp_arr


def col_mult_half(arr, *, max_=float('inf')):
    return col_mult(arr, 0.5, max_=max_)


def col_mult_double(arr, *, max_=float('inf')):
    return col_mult(arr, 2, max_=max_)


def col_grayer(arr):
    circle_avg = max(arr) + 10
    return [(60 * (arr[0] + 15)) // circle_avg + 1,
            (60 * (arr[1]) + 15) // circle_avg + 1,
            (60 * (arr[2]) + 15) // circle_avg + 1]


def angle_gen(num_angles, start_angle=0):
    """yields the angles around a unit circle, each having a constant angle diff between, starting at the start angle"""
    for i in range(num_angles):
        yield i * math.tau / num_angles + start_angle
