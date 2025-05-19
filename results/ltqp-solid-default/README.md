### Successful queries

| Combination | D-1 | D-2 | D-3 | D-4 | D-5 | D-6 | D-7 | D-8 | S-1 | S-2 | S-3 | S-4 | S-5 | S-6 | S-7 | Total |
| - | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: |
| file-per-date | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 2 | 5 | 5 | 2 | 1 | 65 |
| file-per-location | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 2 | 5 | 5 | 1 | 0 | 63 |
| file-per-resource | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 5 | 5 | 2 | 5 | 5 | 5 | 5 | 1 | 47 |
| mixed | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 2 | 5 | 5 | 1 | 1 | 64 |
| single-file | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 2 | 5 | 5 | 0 | 1 | 63 |

### Query processing

![processing](./processing.svg)

| Combination | *dieff@full* | *dieff@full* min | *dieff@full* max | Duration | Duration min | Duration max | First result | First result min | First result max | Last result | Last result min | Last result max | Queries | Results |
| - | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: | -: |
| file-per-date | 364264.975 | 88274.000 | 1116005.500 | 119.553 | 67.527 | 223.381 | 89.091 | 35.475 | 202.363 | 168.796 | 112.161 | 389.681 | 38 | 812 |
| file-per-location | 388882.950 | 95434.500 | 1030504.000 | 228.503 | 55.521 | 462.208 | 141.686 | 73.144 | 317.254 | 260.156 | 207.959 | 531.635 | 38 | 811 |
| file-per-resource | 478481.700 | 233851.500 | 794156.000 | 170.761 | 95.048 | 281.030 | 29.935 | 22.725 | 39.756 | 193.362 | 158.564 | 309.812 | 38 | 802 |
| mixed | 742200.300 | 277891.500 | 1388679.500 | 336.982 | 119.458 | 769.657 | 171.479 | 25.015 | 494.945 | 351.572 | 226.954 | 748.582 | 38 | 813 |
| single-file | 606480.058 | 192542.500 | 1417215.000 | 315.585 | 109.532 | 625.389 | 192.800 | 48.432 | 433.660 | 342.614 | 127.034 | 693.412 | 38 | 813 |

### Network usage

![network](./resources.svg)

| Combination | HTTP requests | HTTP requests min | HTTP requests max | Total data transfer (GB) | Queries |
| - | -: | -: | -: | -: | -: |
| file-per-date | 22845 | 15860 | 35394 | 56.096 | 38 |
| file-per-location | 36835 | 30227 | 44942 | 127.548 | 38 |
| file-per-resource | 16967 | 15079 | 22421 | 23.295 | 38 |
| mixed | 39349 | 24241 | 71494 | 83.457 | 38 |
| single-file | 28777 | 18158 | 39311 | 144.266 | 38 |

### Resource usage

| Combination | Total duration (s) | Total CPU-seconds (%) | Total GB-seconds | Queries |
| - | -: | -: | -: | -: |
| file-per-date | 20946 | 404740 | 104894 | 75 |
| file-per-location | 23401 | 418203 | 146904 | 75 |
| file-per-resource | 15777 | 236666 | 38286 | 75 |
| mixed | 26333 | 516173 | 211848 | 75 |
| single-file | 25026 | 440011 | 182217 | 75 |