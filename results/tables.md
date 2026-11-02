# Main results

Times are medians of three instance medians. Each instance has nine timed batches.
IQR spans the three instance medians using inclusive linear interpolation. Units: microseconds per search.

| Configuration | Naive median (IQR) | KMP median (IQR) | Naive / KMP time |
| --- | --- | --- | --- |
| Repeated absent, n=65,536 m=512 | 11159.800 (11131.500-11185.650) | 104.502 (104.379-105.132) | 106.79 |
| Repeated absent, n=262,144 m=32 | 2872.040 (2865.730-2896.435) | 427.293 (426.819-429.000) | 6.72 |
| Random alphabet 2 absent, n=262,144 m=32 | 1089.250 (1086.480-1098.790) | 1011.920 (1010.875-1017.345) | 1.08 |
| Random alphabet 26 absent, n=262,144 m=32 | 246.156 (244.589-248.982) | 253.849 (253.328-260.792) | 0.97 |
| Prose absent, n=262,144 m=32 | 212.995 (201.786-237.055) | 219.360 (211.123-238.519) | 0.97 |
| Repeated beginning, n=65,536 m=512 | 0.170 (0.170-0.172) | 0.510 (0.510-0.517) | 0.33 |
