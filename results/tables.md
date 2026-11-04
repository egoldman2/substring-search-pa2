# Main results

Times are medians of three instance medians. Each instance has nine timed batches.
IQR spans the three instance medians using inclusive linear interpolation. Units: microseconds per search.

| Configuration | Naive median (IQR) | KMP median (IQR) | Naive / KMP time |
| --- | --- | --- | --- |
| Repeated absent, n=65,536 m=512 | 11143.000 (11135.450-11203.200) | 106.656 (106.227-107.307) | 104.48 |
| Repeated absent, n=262,144 m=32 | 2878.210 (2877.750-2879.875) | 432.520 (430.239-432.567) | 6.65 |
| Random alphabet 2 absent, n=262,144 m=32 | 1088.710 (1084.855-1090.395) | 1008.210 (997.835-1024.190) | 1.08 |
| Random alphabet 26 absent, n=262,144 m=32 | 241.521 (240.750-242.524) | 249.271 (248.474-251.818) | 0.97 |
| Prose absent, n=262,144 m=32 | 209.474 (193.810-234.169) | 209.396 (194.933-235.104) | 1.00 |
| Repeated beginning, n=65,536 m=512 | 0.171 (0.171-0.171) | 0.506 (0.505-0.508) | 0.34 |
