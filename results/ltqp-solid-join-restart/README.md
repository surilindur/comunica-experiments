## Combinations

| Combination | Duration (s) | First result (s) | Last result (s) | dieff@full | HTTP requests | CPU-seconds (%) | GB-seconds | Network ingress (GB) | Network egress (GB) | Total results |
|:-|-:|-:|-:|-:|-:|-:|-:|-:|-:|-:|
| baseline-0ms | 0.49 | 0.33 | 0.39 | 1.50 | 61.71 | 62343.64 | 15800.84 | 1.61 | 31.47 | 644.00 |
| baseline-50ms | 0.82 | 0.64 | 0.71 | 1.95 | 61.71 | 203678.54 | 41662.97 | 28.90 | 1.54 | 644.00 |
| baseline-100ms | 1.09 | 0.88 | 0.94 | 1.57 | 61.71 | 217613.52 | 44028.94 | 29.05 | 1.50 | 644.00 |
| overhead-hagedorn-0ms | 0.55 | 0.38 | 0.45 | 1.84 | 61.71 | 193235.94 | 38892.02 | 27.23 | 0.84 | 644.00 |
| overhead-hagedorn-50ms | 0.86 | 0.68 | 0.75 | 2.20 | 61.71 | 43885.42 | 6617.78 | 0.84 | 26.60 | 644.00 |
| overhead-hagedorn-100ms | 1.11 | 0.90 | 0.98 | 2.56 | 61.71 | 39279.59 | 5821.05 | 0.70 | 24.86 | 644.00 |
| overhead-predicate-0ms | 0.54 | 0.38 | 0.45 | 1.99 | 61.71 | 194023.85 | 37624.33 | 26.76 | 0.80 | 644.00 |
| overhead-predicate-50ms | 0.85 | 0.67 | 0.74 | 2.28 | 61.71 | 42646.77 | 6998.13 | 0.78 | 25.96 | 644.00 |
| overhead-predicate-100ms | 1.12 | 0.92 | 0.99 | 2.27 | 61.71 | 40524.10 | 10778.53 | 0.74 | 25.32 | 644.00 |
| restart-100ms-hagedorn | 0.86 | 0.70 | 0.78 | 2.00 | 61.71 | 312396.45 | 79241.60 | 26.66 | 1.76 | 644.00 |
| restart-100ms-hagedorn-once | 0.81 | 0.66 | 0.73 | 2.13 | 61.71 | 57093.66 | 14764.75 | 1.55 | 25.90 | 644.00 |
| restart-100ms-predicate | 0.55 | 0.38 | 0.45 | 1.80 | 86.64 | 229757.09 | 51322.82 | 26.89 | 1.81 | 644.00 |
| restart-100ms-predicate-once | 0.43 | 0.27 | 0.34 | 1.68 | 61.71 | 240728.87 | 57610.03 | 26.65 | 1.76 | 644.00 |
| restart-1000ms-hagedorn | 0.54 | 0.38 | 0.45 | 2.07 | 61.71 | 224702.36 | 46206.59 | 25.80 | 1.64 | 644.00 |
| restart-1000ms-hagedorn-once | 0.53 | 0.37 | 0.44 | 1.95 | 61.71 | 242955.32 | 51565.84 | 25.38 | 1.64 | 644.00 |
| restart-1000ms-predicate | 0.52 | 0.37 | 0.44 | 1.99 | 61.71 | 61620.70 | 15345.98 | 1.83 | 27.25 | 644.00 |
| restart-1000ms-predicate-once | 0.53 | 0.37 | 0.44 | 1.79 | 61.71 | 62003.23 | 13622.96 | 2.03 | 27.86 | 644.00 |
| restart-10000ms-hagedorn | 0.57 | 0.41 | 0.48 | 1.60 | 61.71 | 67427.26 | 15587.81 | 1.93 | 29.63 | 644.00 |
| restart-10000ms-hagedorn-once | 0.55 | 0.38 | 0.46 | 2.18 | 61.71 | 67141.05 | 18240.02 | 1.91 | 31.33 | 644.00 |
| restart-10000ms-predicate | 0.53 | 0.37 | 0.44 | 1.97 | 61.71 | 237755.22 | 55339.02 | 29.96 | 1.99 | 644.00 |
| restart-10000ms-predicate-once | 0.54 | 0.39 | 0.46 | 2.21 | 61.71 | 68936.68 | 19838.78 | 2.00 | 31.29 | 644.00 |
| restart-update-hagedorn-0ms | 0.83 | 0.67 | 0.74 | 1.77 | 61.71 | 61127.00 | 16147.32 | 1.79 | 26.93 | 644.00 |
| restart-update-hagedorn-50ms | 1.07 | 0.91 | 0.98 | 3.16 | 61.71 | 59143.03 | 14739.52 | 1.65 | 26.94 | 644.00 |
| restart-update-hagedorn-100ms | 1.57 | 1.36 | 1.43 | 2.65 | 61.71 | 58625.58 | 13574.08 | 1.60 | 25.86 | 644.00 |
| restart-update-predicate-0ms | 0.44 | 0.28 | 0.36 | 2.15 | 61.71 | 54514.54 | 14315.77 | 3.84 | 0.18 | 644.00 |
| restart-update-predicate-50ms | 0.71 | 0.54 | 0.61 | 2.26 | 61.74 | 63801.62 | 15927.54 | 2.07 | 29.10 | 644.00 |
| restart-update-predicate-100ms | 0.98 | 0.79 | 0.86 | 2.28 | 61.71 | 189849.21 | 41207.39 | 26.89 | 1.84 | 644.00 |

## templates

![templates](templates.svg)

## combinations

![combinations](combinations.svg)

## httprequests

![httprequests](httprequests.svg)

## diefficiency

![diefficiency](diefficiency.svg)

## timestamps

![timestamps](timestamps.svg)

## durations

![durations](durations.svg)

## resources

![resources](resources.svg)

