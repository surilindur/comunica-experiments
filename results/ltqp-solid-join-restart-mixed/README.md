## Combinations

| Combination | Duration (s) | First result (s) | Last result (s) | dieff@full | HTTP requests | CPU-seconds (%) | GB-seconds | Network ingress (GB) | Network egress (GB) | Total results |
|:-|-:|-:|-:|-:|-:|-:|-:|-:|-:|-:|
| baseline | 1.04 | 0.69 | 0.77 | 1.38 | 53.82 | 10319.22 | 1779.92 | 0.08 | 3.80 | 383.00 |
| overhead-hagedorn | 0.97 | 0.32 | 0.42 | 1.41 | 59.94 | 7189.41 | 1246.91 | 0.06 | 2.52 | 383.00 |
| overhead-hagedorn-latency-50 | 1.09 | 0.52 | 0.62 | 1.68 | 47.21 | 8177.52 | 1200.34 | 0.06 | 2.58 | 383.00 |
| overhead-hagedorn-latency-100 | 1.25 | 0.74 | 0.84 | 1.50 | 47.21 | 45184.94 | 5022.09 | 2.52 | 0.06 | 383.00 |
| overhead-hagedorn-latency-300 | 1.96 | 1.45 | 1.55 | 1.86 | 47.21 | 45859.64 | 5145.67 | 2.67 | 0.06 | 383.00 |
| overhead-predicate | 0.98 | 0.32 | 0.43 | 1.52 | 55.80 | 7473.08 | 1288.95 | 0.06 | 2.68 | 383.00 |
| interval-100-hagedorn | 1.84 | 0.61 | 0.84 | 1.81 | 66.47 | 7938.19 | 1648.50 | 0.07 | 3.21 | 387.00 |
| interval-100-hagedorn-once | 1.11 | 0.96 | 1.29 | 2.13 | 47.21 | 52370.76 | 7253.29 | 3.35 | 0.07 | 387.00 |
| interval-100-predicate | 1.68 | 0.30 | 0.49 | 1.79 | 65.15 | 8091.32 | 1622.77 | 0.07 | 3.55 | 398.00 |
| interval-1000-hagedorn | 1.60 | 0.32 | 0.58 | 1.67 | 59.99 | 8242.03 | 1702.37 | 0.07 | 3.62 | 386.00 |
| interval-1000-hagedorn-once | 1.17 | 0.33 | 0.55 | 1.63 | 47.24 | 47135.12 | 7046.57 | 3.54 | 0.07 | 386.00 |
| interval-1000-predicate | 1.18 | 0.50 | 0.69 | 1.83 | 47.50 | 45427.00 | 6442.45 | 3.54 | 0.07 | 386.00 |
| interval-2000-hagedorn | 1.10 | 0.33 | 0.55 | 1.66 | 47.21 | 7618.62 | 1498.07 | 0.06 | 3.60 | 385.00 |
| interval-2000-hagedorn-once | 1.14 | 0.37 | 0.57 | 1.57 | 47.38 | 8313.49 | 1650.11 | 0.07 | 3.79 | 385.00 |
| interval-2000-predicate | 1.11 | 0.37 | 0.59 | 1.92 | 47.21 | 46057.26 | 6789.44 | 3.57 | 0.07 | 385.00 |
| interval-5000-hagedorn | 1.15 | 0.33 | 0.58 | 1.67 | 47.30 | 8453.01 | 1493.47 | 0.07 | 3.91 | 384.00 |
| interval-5000-hagedorn-once | 1.11 | 0.32 | 0.56 | 1.71 | 47.21 | 49582.45 | 7674.67 | 4.16 | 0.07 | 384.00 |
| interval-5000-predicate | 1.65 | 0.31 | 0.54 | 1.76 | 65.14 | 8651.61 | 1617.98 | 0.07 | 4.06 | 384.00 |
| interval-10000-hagedorn | 1.71 | 0.35 | 0.70 | 1.82 | 92.63 | 8801.18 | 1775.77 | 0.08 | 4.39 | 384.00 |
| interval-10000-hagedorn-once | 1.17 | 0.58 | 0.94 | 1.86 | 47.21 | 54428.84 | 9674.07 | 4.38 | 0.08 | 384.00 |
| interval-10000-predicate | 1.29 | 0.33 | 0.70 | 1.87 | 51.24 | 8684.17 | 1641.50 | 0.08 | 4.31 | 384.00 |
| interval-20000-hagedorn | 1.14 | 0.75 | 0.86 | 1.71 | 47.21 | 8557.49 | 1645.16 | 0.07 | 4.31 | 383.00 |
| interval-20000-hagedorn-once | 1.11 | 0.33 | 0.45 | 1.50 | 47.24 | 52228.86 | 8393.85 | 4.34 | 0.07 | 383.00 |
| interval-20000-predicate | 1.13 | 0.58 | 0.69 | 1.58 | 47.21 | 8430.42 | 1686.69 | 0.07 | 4.39 | 383.00 |
| metadata-hagedorn | 1.13 | 0.54 | 0.65 | 1.64 | 47.24 | 7618.68 | 1563.74 | 0.06 | 3.24 | 383.00 |
| metadata-hagedorn-latency-50 | 1.39 | 0.67 | 0.77 | 1.65 | 47.21 | 7466.20 | 2092.29 | 0.06 | 3.10 | 383.00 |
| metadata-hagedorn-latency-100 | 1.97 | 1.17 | 1.28 | 1.89 | 56.21 | 45129.78 | 6567.72 | 2.99 | 0.06 | 383.00 |
| metadata-hagedorn-latency-300 | 2.15 | 1.50 | 1.60 | 1.72 | 47.21 | 7636.46 | 1636.36 | 0.06 | 2.61 | 383.00 |
| metadata-hagedorn-once | 1.47 | 0.40 | 0.54 | 1.80 | 60.63 | 8033.17 | 1713.13 | 0.07 | 3.58 | 383.00 |
| metadata-predicate | 1.10 | 0.50 | 0.62 | 1.69 | 47.21 | 8129.78 | 1810.85 | 0.07 | 3.47 | 389.00 |

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

