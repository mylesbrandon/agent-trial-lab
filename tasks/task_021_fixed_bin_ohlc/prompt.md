# Task 021: Fixed-bin OHLC Resampling

Implement resample_ohlc(times, prices, width, origin=0). Return a list of
(bin_start, open, high, low, close) tuples, ordered by bin_start, containing
only bins with observations. Never fabricate empty bins.

Bin k begins at origin + k*width and covers the half-open interval
[bin_start, bin_start + width). Use floor division to assign observations,
including timestamps before origin. open and close are respectively the
first and last observed price in input order within a bin; high and low
are its maximum and minimum price. Equal timestamps are allowed and retain
input order, so the last duplicate can set close.

Inputs are lists or tuples of equal length. times must be nondecreasing
Python ints excluding bool; negative timestamps are valid. prices must be
finite Python ints or floats excluding bool, including zero or negative
prices. width is a positive Python int excluding bool and origin is a
Python int excluding bool. Raise ValueError for invalid types, nonfinite
prices, decreasing times, unequal lengths, or invalid width/origin. Check
parameters even on empty inputs. Empty valid inputs return []. Do not
mutate inputs.

Example: times=[0, 2, 5], prices=[10, 12, 7], width=5 produces
[(0, 10, 12, 10, 12), (5, 7, 7, 7, 7)].
