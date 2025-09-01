# Optimizer Summary

## BTCUSDT 4h

Best (score=pnl-lam\*dd): ema | fast=10,slow=200 | risk=0.01 | atr=2.5 | pnl=10363.64 | dd=2800 | trades=77 | eq=20363.64 | cagr=21.40%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BTCUSDT/4h --strategy ema --lookback 1000000 --risk 0.01 --equity 10000 --atr 14 --atr-mult 2.5 --fee-bps 4 --slip-bps 1 --fast 10 --slow 200
```

Top Results

| Strategy  | Params             | Risk | ATR |      PnL |   DD | Trades |   Equity |   CAGR |
| --------- | ------------------ | ---: | --: | -------: | ---: | -----: | -------: | -----: |
| ema       | fast=10,slow=200   | 0.01 | 2.5 | 10363.64 | 2800 |     77 | 20363.64 | 21.40% |
| ema       | fast=10,slow=100   | 0.01 | 2.0 | 10250.95 | 2667 |    121 | 20250.95 | 21.22% |
| ema       | fast=30,slow=50    | 0.01 | 2.0 |  8672.26 | 2419 |    119 | 18672.26 | 18.57% |
| bollinger | period=20,mult=2.0 | 0.01 | 2.0 |  8342.71 | 2616 |    291 | 18342.71 | 17.99% |
| bollinger | period=20,mult=2.5 | 0.01 | 2.5 |  7908.56 | 2609 |    226 | 17908.56 | 17.22% |
| ema       | fast=10,slow=200   | 0.01 | 3.0 |  7598.11 | 2220 |     77 | 17598.11 | 16.67% |
| ema       | fast=30,slow=200   | 0.01 | 2.0 |  7500.52 | 2437 |     55 | 17500.52 | 16.49% |
| ema       | fast=10,slow=100   | 0.01 | 2.5 |  7123.49 | 2185 |    121 | 17123.49 | 15.80% |
| bollinger | period=20,mult=2.0 | 0.01 | 2.5 |  6768.90 | 2001 |    285 | 16768.90 | 15.14% |
| ema       | fast=20,slow=100   | 0.01 | 2.5 |  6960.47 | 2698 |     91 | 16960.47 | 15.50% |

## BTCUSDT 2h

Best (score=pnl-lam\*dd): ema | fast=10,slow=200 | risk=0.01 | atr=3.0 | pnl=9669.14 | dd=2761 | trades=159 | eq=19669.14 | cagr=20.26%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BTCUSDT/2h --strategy ema --lookback 1000000 --risk 0.01 --equity 10000 --atr 14 --atr-mult 3.0 --fee-bps 4 --slip-bps 1 --fast 10 --slow 200
```

Top Results

| Strategy | Params           |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| -------- | ---------------- | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| ema      | fast=10,slow=200 |  0.01 | 3.0 | 9669.14 | 2761 |    159 | 19669.14 | 20.26% |
| ema      | fast=20,slow=200 |  0.01 | 2.5 | 9297.29 | 2565 |    115 | 19297.29 | 19.63% |
| ema      | fast=10,slow=200 |  0.01 | 2.5 | 7360.51 | 2615 |    159 | 17360.51 | 16.23% |
| ema      | fast=20,slow=200 |  0.01 | 3.0 | 6192.24 | 2109 |    115 | 16192.24 | 14.05% |
| ema      | fast=30,slow=200 | 0.005 | 2.5 | 5727.80 | 1501 |    101 | 15727.80 | 13.14% |
| ema      | fast=50,slow=200 |  0.01 | 3.0 | 5678.17 | 2386 |     87 | 15678.17 | 13.05% |
| ema      | fast=10,slow=50  | 0.005 | 2.0 | 5459.36 | 1967 |    419 | 15459.36 | 12.61% |
| ema      | fast=10,slow=100 |  0.01 | 2.5 | 5519.92 | 2707 |    295 | 15519.92 | 12.73% |
| ema      | fast=30,slow=200 | 0.005 | 3.0 | 4505.14 | 1244 |    101 | 14505.14 | 10.67% |
| ema      | fast=10,slow=200 | 0.005 | 3.0 | 4381.43 | 1107 |    159 | 14381.43 | 10.42% |

## BTCUSDT 1h

Best (score=pnl-lam\*dd): bollinger | period=50,mult=3.0 | risk=0.005 | atr=2.0 | pnl=8271.36 | dd=2006 | trades=394 | eq=18271.36 | cagr=17.87%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BTCUSDT/1h --strategy bollinger --lookback 1000000 --risk 0.005 --equity 10000 --atr 14 --atr-mult 2.0 --fee-bps 4 --slip-bps 1 --bb-period 50 --bb-mult 3.0
```

Top Results

| Strategy  | Params             |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| --------- | ------------------ | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| bollinger | period=50,mult=3.0 | 0.005 | 2.0 | 8271.36 | 2006 |    394 | 18271.36 | 17.87% |
| bollinger | period=50,mult=3.0 | 0.005 | 2.5 | 5380.68 | 1703 |    384 | 15380.68 | 12.46% |
| ema       | fast=10,slow=100   | 0.005 | 3.0 | 5337.16 | 2128 |    561 | 15337.16 | 12.37% |
| ema       | fast=20,slow=100   | 0.005 | 3.0 | 5269.84 | 2021 |    417 | 15269.84 | 12.24% |
| bollinger | period=50,mult=3.0 | 0.003 | 2.0 | 4531.49 |  925 |    394 | 14531.49 | 10.73% |
| ema       | fast=50,slow=200   | 0.005 | 3.0 | 4966.92 | 2220 |    185 | 14966.92 | 11.62% |
| bollinger | period=50,mult=2.0 | 0.005 | 2.0 | 4864.27 | 2161 |    635 | 14864.27 | 11.42% |
| bollinger | period=50,mult=3.0 | 0.005 | 3.0 | 4146.27 | 1447 |    379 | 14146.27 |  9.92% |
| ema       | fast=20,slow=200   | 0.005 | 3.0 | 4003.62 | 1546 |    297 | 14003.62 |  9.62% |
| bollinger | period=50,mult=2.5 | 0.005 | 3.0 | 3871.39 | 1562 |    492 | 13871.39 |  9.33% |

## BTCUSDT 30m

Best (score=pnl-lam\*dd): ema | fast=30,slow=200 | risk=0.005 | atr=3.0 | pnl=3657.74 | dd=2770 | trades=493 | eq=13657.74 | cagr=8.87%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BTCUSDT/30m --strategy ema --lookback 1000000 --risk 0.005 --equity 10000 --atr 14 --atr-mult 3.0 --fee-bps 4 --slip-bps 1 --fast 30 --slow 200
```

Top Results

| Strategy  | Params                            |  Risk | ATR |     PnL |   DD | Trades |   Equity |  CAGR |
| --------- | --------------------------------- | ----: | --: | ------: | ---: | -----: | -------: | ----: |
| ema       | fast=30,slow=200                  | 0.005 | 3.0 | 3657.74 | 2770 |    493 | 13657.74 | 8.87% |
| ema       | fast=30,slow=200                  | 0.003 | 3.0 | 2287.33 | 1434 |    493 | 12287.33 | 5.78% |
| ema       | fast=20,slow=200                  | 0.003 | 2.5 | 2127.50 | 2078 |    569 | 12127.50 | 5.40% |
| bollinger | period=50,mult=3.0                | 0.003 | 2.0 | 1802.39 | 1710 |    787 | 11802.39 | 4.62% |
| ema       | fast=50,slow=200                  | 0.003 | 3.0 | 1135.52 | 1642 |    391 | 11135.52 | 2.98% |
| ema       | fast=20,slow=200                  | 0.003 | 3.0 | 1235.31 | 1998 |    569 | 11235.31 | 3.23% |
| ema       | fast=50,slow=200                  | 0.005 | 3.0 | 1733.05 | 2997 |    391 | 11733.05 | 4.45% |
| bollinger | period=50,mult=3.0                | 0.003 | 3.0 |  780.90 | 1402 |    752 | 10780.90 | 2.07% |
| rsi       | period=14,eL=25.0,xL=55.0,ema=200 |  0.01 | 2.0 |  118.74 |  185 |     12 | 10118.74 | 0.32% |
| rsi       | period=14,eL=25.0,xL=55.0,ema=200 |  0.01 | 2.5 |   95.19 |  148 |     12 | 10095.19 | 0.26% |

## BTCUSDT 15m

Best (score=pnl-lam\*dd): rsi | period=14,eL=25.0,xL=55.0,ema=200 | risk=0.003 | atr=3.0 | pnl=-191.43 | dd=211 | trades=22 | eq=9808.57 | cagr=-0.53%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BTCUSDT/15m --strategy rsi --lookback 1000000 --risk 0.003 --equity 10000 --atr 14 --atr-mult 3.0 --fee-bps 4 --slip-bps 1 --rsi-period 14 --rsi-entry 25.0 --rsi-exit 55.0 --rsi-ema 200
```

Top Results

| Strategy | Params                            |  Risk | ATR |     PnL |  DD | Trades |  Equity |   CAGR |
| -------- | --------------------------------- | ----: | --: | ------: | --: | -----: | ------: | -----: |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 3.0 | -191.43 | 211 |     22 | 9808.57 | -0.53% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.003 | 3.0 | -202.52 | 222 |     22 | 9797.48 | -0.56% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 2.5 | -246.39 | 270 |     22 | 9753.61 | -0.68% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.003 | 2.5 | -290.78 | 313 |     22 | 9709.22 | -0.80% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.005 | 3.0 | -317.49 | 350 |     22 | 9682.51 | -0.88% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 2.0 | -322.35 | 352 |     22 | 9677.65 | -0.89% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.005 | 3.0 | -335.78 | 367 |     22 | 9664.22 | -0.93% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.003 | 2.0 | -366.80 | 395 |     22 | 9633.20 | -1.01% |
| rsi      | period=14,eL=30.0,xL=55.0,ema=200 | 0.003 | 3.0 | -408.70 | 439 |    113 | 9591.30 | -1.13% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.005 | 2.5 | -407.89 | 446 |     22 | 9592.11 | -1.13% |

## ETHUSDT 4h

Best (score=pnl-lam\*dd): ema | fast=20,slow=100 | risk=0.01 | atr=2.0 | pnl=6018.69 | dd=2463 | trades=102 | eq=16018.69 | cagr=13.71%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair ETHUSDT/4h --strategy ema --lookback 1000000 --risk 0.01 --equity 10000 --atr 14 --atr-mult 2.0 --fee-bps 4 --slip-bps 1 --fast 20 --slow 100
```

Top Results

| Strategy  | Params             | Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| --------- | ------------------ | ---: | --: | ------: | ---: | -----: | -------: | -----: |
| ema       | fast=20,slow=100   | 0.01 | 2.0 | 6018.69 | 2463 |    102 | 16018.69 | 13.71% |
| bollinger | period=50,mult=2.5 | 0.01 | 2.0 | 5764.90 | 1999 |    112 | 15764.90 | 13.22% |
| ema       | fast=10,slow=50    | 0.01 | 2.0 | 5693.01 | 2203 |    221 | 15693.01 | 13.08% |
| bollinger | period=50,mult=2.5 | 0.01 | 2.5 | 5321.55 | 1806 |    108 | 15321.55 | 12.34% |
| ema       | fast=10,slow=200   | 0.01 | 3.0 | 5173.37 | 2145 |     78 | 15173.37 | 12.04% |
| bollinger | period=50,mult=3.0 | 0.01 | 2.0 | 4856.46 | 1831 |     84 | 14856.46 | 11.40% |
| bollinger | period=50,mult=3.0 | 0.01 | 2.5 | 4715.87 | 1739 |     82 | 14715.87 | 11.11% |
| ema       | fast=20,slow=100   | 0.01 | 3.0 | 4665.51 | 1834 |    102 | 14665.51 | 11.01% |
| ema       | fast=30,slow=100   | 0.01 | 2.5 | 4866.33 | 2247 |     76 | 14866.33 | 11.42% |
| bollinger | period=50,mult=2.5 | 0.01 | 3.0 | 4413.08 | 1591 |    106 | 14413.08 | 10.48% |

## ETHUSDT 2h

Best (score=pnl-lam\*dd): ema | fast=30,slow=100 | risk=0.01 | atr=3.0 | pnl=8412.52 | dd=2056 | trades=181 | eq=18412.52 | cagr=18.11%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair ETHUSDT/2h --strategy ema --lookback 1000000 --risk 0.01 --equity 10000 --atr 14 --atr-mult 3.0 --fee-bps 4 --slip-bps 1 --fast 30 --slow 100
```

Top Results

| Strategy  | Params             |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| --------- | ------------------ | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| ema       | fast=30,slow=100   |  0.01 | 3.0 | 8412.52 | 2056 |    181 | 18412.52 | 18.11% |
| ema       | fast=20,slow=200   |  0.01 | 3.0 | 7078.35 | 2695 |    132 | 17078.35 | 15.72% |
| ema       | fast=30,slow=200   |  0.01 | 2.5 | 6925.53 | 2930 |    102 | 16925.53 | 15.43% |
| ema       | fast=30,slow=100   |  0.01 | 2.5 | 6445.61 | 2222 |    181 | 16445.61 | 14.53% |
| ema       | fast=20,slow=200   | 0.005 | 2.0 | 6074.21 | 1664 |    132 | 16074.21 | 13.82% |
| bollinger | period=50,mult=3.0 |  0.01 | 2.0 | 6329.26 | 2391 |    182 | 16329.26 | 14.31% |
| ema       | fast=10,slow=200   |  0.01 | 3.0 | 6231.26 | 2664 |    200 | 16231.26 | 14.12% |
| bollinger | period=50,mult=2.0 |  0.01 | 2.5 | 5718.85 | 2568 |    292 | 15718.85 | 13.13% |
| ema       | fast=30,slow=200   | 0.005 | 2.0 | 4857.04 | 1449 |    102 | 14857.04 | 11.40% |
| ema       | fast=30,slow=100   | 0.005 | 2.0 | 4698.07 | 1178 |    181 | 14698.07 | 11.07% |

## ETHUSDT 1h

Best (score=pnl-lam\*dd): ema | fast=50,slow=200 | risk=0.01 | atr=3.0 | pnl=6147.62 | dd=2786 | trades=204 | eq=16147.62 | cagr=13.96%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair ETHUSDT/1h --strategy ema --lookback 1000000 --risk 0.01 --equity 10000 --atr 14 --atr-mult 3.0 --fee-bps 4 --slip-bps 1 --fast 50 --slow 200
```

Top Results

| Strategy  | Params             |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| --------- | ------------------ | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| ema       | fast=50,slow=200   |  0.01 | 3.0 | 6147.62 | 2786 |    204 | 16147.62 | 13.96% |
| ema       | fast=20,slow=200   | 0.005 | 2.0 | 5312.66 | 2059 |    312 | 15312.66 | 12.32% |
| ema       | fast=20,slow=50    | 0.005 | 3.0 | 4742.54 | 2037 |    617 | 14742.54 | 11.17% |
| ema       | fast=20,slow=200   | 0.005 | 3.0 | 4462.73 | 1817 |    312 | 14462.73 | 10.59% |
| ema       | fast=20,slow=200   | 0.005 | 2.5 | 4448.94 | 2000 |    312 | 14448.94 | 10.56% |
| ema       | fast=20,slow=50    | 0.005 | 2.5 | 4433.08 | 2001 |    617 | 14433.08 | 10.52% |
| ema       | fast=30,slow=200   | 0.005 | 3.0 | 4127.33 | 1453 |    272 | 14127.33 |  9.88% |
| bollinger | period=50,mult=2.0 | 0.005 | 2.0 | 4466.88 | 2150 |    627 | 14466.88 | 10.60% |
| ema       | fast=10,slow=50    | 0.005 | 3.0 | 4404.96 | 2546 |    866 | 14404.96 | 10.47% |
| ema       | fast=30,slow=200   | 0.005 | 2.0 | 4169.75 | 2264 |    272 | 14169.75 |  9.97% |

## ETHUSDT 30m

Best (score=pnl-lam\*dd): ema | fast=10,slow=200 | risk=0.003 | atr=2.0 | pnl=7794.76 | dd=2640 | trades=745 | eq=17794.76 | cagr=17.02%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair ETHUSDT/30m --strategy ema --lookback 1000000 --risk 0.003 --equity 10000 --atr 14 --atr-mult 2.0 --fee-bps 4 --slip-bps 1 --fast 10 --slow 200
```

Top Results

| Strategy  | Params             |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| --------- | ------------------ | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| ema       | fast=10,slow=200   | 0.003 | 2.0 | 7794.76 | 2640 |    745 | 17794.76 | 17.02% |
| ema       | fast=10,slow=200   | 0.003 | 2.5 | 5252.11 | 2486 |    745 | 15252.11 | 12.20% |
| ema       | fast=20,slow=200   | 0.003 | 2.0 | 4652.64 | 2151 |    593 | 14652.64 | 10.98% |
| ema       | fast=10,slow=200   | 0.003 | 3.0 | 4590.88 | 2061 |    745 | 14590.88 | 10.85% |
| ema       | fast=30,slow=200   | 0.003 | 2.0 | 4159.63 | 2513 |    491 | 14159.63 |  9.95% |
| ema       | fast=20,slow=100   | 0.003 | 2.0 | 4130.49 | 2598 |    879 | 14130.49 |  9.89% |
| ema       | fast=30,slow=200   | 0.003 | 2.5 | 3471.90 | 2022 |    491 | 13471.90 |  8.47% |
| bollinger | period=50,mult=3.0 | 0.005 | 2.5 | 3566.69 | 2601 |    745 | 13566.69 |  8.67% |
| bollinger | period=50,mult=3.0 | 0.003 | 2.0 | 2949.57 | 1733 |    764 | 12949.57 |  7.30% |
| ema       | fast=50,slow=100   | 0.003 | 2.0 | 2834.83 | 1588 |    546 | 12834.83 |  7.04% |

## ETHUSDT 15m

Best (score=pnl-lam\*dd): ema | fast=50,slow=200 | risk=0.003 | atr=2.5 | pnl=1680.84 | dd=2444 | trades=773 | eq=11680.84 | cagr=4.33%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair ETHUSDT/15m --strategy ema --lookback 1000000 --risk 0.003 --equity 10000 --atr 14 --atr-mult 2.5 --fee-bps 4 --slip-bps 1 --fast 50 --slow 200
```

Top Results

| Strategy | Params                            |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| -------- | --------------------------------- | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| ema      | fast=50,slow=200                  | 0.003 | 2.5 | 1680.84 | 2444 |    773 | 11680.84 |  4.33% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.003 | 3.0 |  -73.62 |  166 |     24 |  9926.38 | -0.20% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.003 | 2.5 |  -76.58 |  185 |     24 |  9923.42 | -0.21% |
| ema      | fast=50,slow=200                  | 0.003 | 3.0 |  844.41 | 2061 |    773 | 10844.41 |  2.24% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 3.0 | -116.11 |  192 |     24 |  9883.89 | -0.32% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 2.5 | -121.43 |  213 |     24 |  9878.57 | -0.33% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.005 | 3.0 | -122.86 |  275 |     24 |  9877.14 | -0.34% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.005 | 2.5 | -127.92 |  307 |     24 |  9872.08 | -0.35% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 2.0 | -174.03 |  288 |     24 |  9825.97 | -0.48% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.003 | 2.0 | -170.22 |  307 |     24 |  9829.78 | -0.47% |

## BNBUSDT 4h

Best (score=pnl-lam\*dd): bollinger | period=50,mult=2.0 | risk=0.01 | atr=2.5 | pnl=5561.05 | dd=1821 | trades=131 | eq=15561.05 | cagr=12.82%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BNBUSDT/4h --strategy bollinger --lookback 1000000 --risk 0.01 --equity 10000 --atr 14 --atr-mult 2.5 --fee-bps 4 --slip-bps 1 --bb-period 50 --bb-mult 2.0
```

Top Results

| Strategy  | Params             |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| --------- | ------------------ | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| bollinger | period=50,mult=2.0 |  0.01 | 2.5 | 5561.05 | 1821 |    131 | 15561.05 | 12.82% |
| ema       | fast=10,slow=50    |  0.01 | 3.0 | 5507.52 | 2682 |    192 | 15507.52 | 12.71% |
| bollinger | period=50,mult=2.0 |  0.01 | 2.0 | 5227.34 | 2851 |    144 | 15227.34 | 12.15% |
| bollinger | period=50,mult=2.0 |  0.01 | 3.0 | 4281.76 | 1444 |    131 | 14281.76 | 10.21% |
| ema       | fast=10,slow=50    | 0.005 | 2.0 | 3904.38 | 1868 |    192 | 13904.38 |  9.41% |
| ema       | fast=10,slow=50    | 0.005 | 2.5 | 3231.72 | 1486 |    192 | 13231.72 |  7.94% |
| ema       | fast=10,slow=100   |  0.01 | 3.0 | 3508.32 | 2201 |    142 | 13508.32 |  8.55% |
| bollinger | period=20,mult=2.0 |  0.01 | 2.0 | 3378.47 | 1984 |    305 | 13378.47 |  8.26% |
| bollinger | period=20,mult=2.0 |  0.01 | 2.5 | 2965.03 | 1449 |    299 | 12965.03 |  7.34% |
| ema       | fast=10,slow=100   |  0.01 | 2.5 | 3501.01 | 2588 |    142 | 13501.01 |  8.53% |

## BNBUSDT 2h

Best (score=pnl-lam\*dd): ema | fast=30,slow=50 | risk=0.01 | atr=2.0 | pnl=9003.41 | dd=2586 | trades=231 | eq=19003.41 | cagr=19.14%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BNBUSDT/2h --strategy ema --lookback 1000000 --risk 0.01 --equity 10000 --atr 14 --atr-mult 2.0 --fee-bps 4 --slip-bps 1 --fast 30 --slow 50
```

Top Results

| Strategy | Params           |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| -------- | ---------------- | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| ema      | fast=30,slow=50  |  0.01 | 2.0 | 9003.41 | 2586 |    231 | 19003.41 | 19.14% |
| ema      | fast=30,slow=50  |  0.01 | 2.5 | 8210.65 | 2356 |    231 | 18210.65 | 17.76% |
| ema      | fast=10,slow=100 |  0.01 | 3.0 | 7391.74 | 2369 |    262 | 17391.74 | 16.29% |
| ema      | fast=30,slow=50  |  0.01 | 3.0 | 7100.57 | 2237 |    231 | 17100.57 | 15.76% |
| ema      | fast=10,slow=100 |  0.01 | 2.5 | 5987.84 | 2542 |    262 | 15987.84 | 13.65% |
| ema      | fast=20,slow=50  | 0.005 | 2.0 | 5188.86 | 1848 |    301 | 15188.86 | 12.07% |
| ema      | fast=10,slow=50  |  0.01 | 3.0 | 5616.67 | 2716 |    417 | 15616.67 | 12.93% |
| ema      | fast=30,slow=50  | 0.005 | 2.0 | 4219.28 | 1180 |    231 | 14219.28 | 10.08% |
| ema      | fast=10,slow=100 | 0.005 | 2.0 | 4103.12 | 1355 |    262 | 14103.12 |  9.83% |
| ema      | fast=20,slow=200 | 0.005 | 2.0 | 4568.45 | 2640 |    146 | 14568.45 | 10.81% |

## BNBUSDT 1h

Best (score=pnl-lam\*dd): ema | fast=20,slow=200 | risk=0.005 | atr=2.5 | pnl=5846.17 | dd=1790 | trades=268 | eq=15846.17 | cagr=13.38%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BNBUSDT/1h --strategy ema --lookback 1000000 --risk 0.005 --equity 10000 --atr 14 --atr-mult 2.5 --fee-bps 4 --slip-bps 1 --fast 20 --slow 200
```

Top Results

| Strategy  | Params             |  Risk | ATR |     PnL |   DD | Trades |   Equity |   CAGR |
| --------- | ------------------ | ----: | --: | ------: | ---: | -----: | -------: | -----: |
| ema       | fast=20,slow=200   | 0.005 | 2.5 | 5846.17 | 1790 |    268 | 15846.17 | 13.38% |
| ema       | fast=20,slow=200   | 0.005 | 3.0 | 4717.08 | 1333 |    268 | 14717.08 | 11.11% |
| ema       | fast=30,slow=200   |  0.01 | 3.0 | 4668.86 | 2918 |    224 | 14668.86 | 11.01% |
| ema       | fast=50,slow=100   | 0.005 | 3.0 | 3582.33 | 1356 |    262 | 13582.33 |  8.71% |
| ema       | fast=20,slow=200   | 0.003 | 2.5 | 3321.68 |  904 |    268 | 13321.68 |  8.14% |
| ema       | fast=10,slow=200   | 0.005 | 2.5 | 4201.98 | 2944 |    426 | 14201.98 | 10.04% |
| ema       | fast=20,slow=200   | 0.005 | 2.0 | 3525.12 | 1763 |    268 | 13525.12 |  8.58% |
| bollinger | period=50,mult=3.0 | 0.005 | 2.0 | 3223.99 | 1652 |    351 | 13223.99 |  7.92% |
| ema       | fast=20,slow=200   | 0.003 | 3.0 | 2705.47 |  705 |    268 | 12705.47 |  6.75% |
| ema       | fast=30,slow=100   | 0.005 | 2.5 | 3593.80 | 2658 |    342 | 13593.80 |  8.73% |

## BNBUSDT 30m

Best (score=pnl-lam\*dd): ema | fast=20,slow=200 | risk=0.003 | atr=3.0 | pnl=1391.79 | dd=2194 | trades=593 | eq=11391.79 | cagr=3.62%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BNBUSDT/30m --strategy ema --lookback 1000000 --risk 0.003 --equity 10000 --atr 14 --atr-mult 3.0 --fee-bps 4 --slip-bps 1 --fast 20 --slow 200
```

Top Results

| Strategy | Params                            |  Risk | ATR |     PnL |   DD | Trades |   Equity |  CAGR |
| -------- | --------------------------------- | ----: | --: | ------: | ---: | -----: | -------: | ----: |
| ema      | fast=20,slow=200                  | 0.003 | 3.0 | 1391.79 | 2194 |    593 | 11391.79 | 3.62% |
| ema      | fast=30,slow=200                  | 0.003 | 3.0 |  795.69 | 1423 |    473 | 10795.69 | 2.11% |
| rsi      | period=14,eL=30.0,xL=50.0,ema=200 |  0.01 | 2.0 |  297.56 |  439 |     53 | 10297.56 | 0.80% |
| rsi      | period=14,eL=30.0,xL=50.0,ema=200 | 0.005 | 2.0 |  152.65 |  216 |     53 | 10152.65 | 0.41% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 |  0.01 | 2.5 |   54.81 |   53 |      3 | 10054.81 | 0.15% |
| rsi      | period=14,eL=30.0,xL=50.0,ema=200 | 0.003 | 2.0 |   92.50 |  129 |     53 | 10092.50 | 0.25% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 |  0.01 | 3.0 |   45.68 |   44 |      3 | 10045.68 | 0.12% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.005 | 2.5 |   27.42 |   26 |      3 | 10027.42 | 0.07% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 |  0.01 | 2.5 |   44.78 |   62 |      3 | 10044.78 | 0.12% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 | 0.005 | 3.0 |   22.85 |   22 |      3 | 10022.85 | 0.06% |

## BNBUSDT 15m

Best (score=pnl-lam\*dd): rsi | period=14,eL=25.0,xL=55.0,ema=200 | risk=0.01 | atr=2.0 | pnl=299.54 | dd=192 | trades=12 | eq=10299.54 | cagr=0.81%

Reproduce:

```bash
python -m qryptify_strategy.backtest --pair BNBUSDT/15m --strategy rsi --lookback 1000000 --risk 0.01 --equity 10000 --atr 14 --atr-mult 2.0 --fee-bps 4 --slip-bps 1 --rsi-period 14 --rsi-entry 25.0 --rsi-exit 55.0 --rsi-ema 200
```

Top Results

| Strategy | Params                            |  Risk | ATR |    PnL |  DD | Trades |   Equity |  CAGR |
| -------- | --------------------------------- | ----: | --: | -----: | --: | -----: | -------: | ----: |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 |  0.01 | 2.0 | 299.54 | 192 |     12 | 10299.54 | 0.81% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 |  0.01 | 2.5 | 218.99 | 152 |     12 | 10218.99 | 0.59% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.005 | 2.0 | 149.80 |  95 |     12 | 10149.80 | 0.41% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 |  0.01 | 3.0 | 165.47 | 126 |     12 | 10165.47 | 0.45% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.005 | 2.5 | 109.68 |  75 |     12 | 10109.68 | 0.30% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 2.0 |  89.88 |  56 |     12 | 10089.88 | 0.24% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.005 | 3.0 |  82.98 |  63 |     12 | 10082.98 | 0.23% |
| rsi      | period=14,eL=25.0,xL=50.0,ema=200 |  0.01 | 2.0 | 159.00 | 220 |     12 | 10159.00 | 0.43% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 2.5 |  65.85 |  45 |     12 | 10065.85 | 0.18% |
| rsi      | period=14,eL=25.0,xL=55.0,ema=200 | 0.003 | 3.0 |  49.84 |  37 |     12 | 10049.84 | 0.14% |
