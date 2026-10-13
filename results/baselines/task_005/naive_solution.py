import math

def stable_softmax(scores):
    values = [math.exp(x) for x in scores]
    total = sum(values)
    return [x / total for x in values]
