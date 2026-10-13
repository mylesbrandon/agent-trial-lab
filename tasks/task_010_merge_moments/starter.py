def merge_moments(left, right):
    a, ma, sa = left
    b, mb, sb = right
    return a + b, (ma + mb) / 2, sa + sb
