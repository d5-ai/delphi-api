# Delphi API

BASE_URL = https://delphi-stats-api.herokuapp.com/

## Endpoints

### GET /apy

This gets the native token apy of each pool

It is calculated by taking the APR and Duration of the last 10 withdraw/deposit events by block

#### Example Request

https://delphi-stats-api.herokuapp.com/apy

#### Example Response

```
{
  "0x051e3a47724740d47042edc71c0ae81a35fdede9": 3.562414425476534,
  "0x08ddb58d31c08242cd444bb5b43f7d2c6bca0396": 4.7646549904520255,
  "0x7967ada2a32a633d5c055e2e075a83023b632b4e": 21.992668362920426,
  "0x91d7b9a8d2314110d4018c88dbfdcf5e2ba4772e": 22.679395295363236,
  "0x9984d588ef2112894a0513663ba815310d383e3c": 2.628552914099433,
  "0xbed50f08b8e68293bd7db742c4207f2f6e520cd2": 11.298503076965972,
  "0xeae1a8206f68a7ef629e85fc69e82cfd36e83ba4": 31.587393071579612
}

```

### GET /liquidity

This gets the current liquidity of the pool (current balance)

#### Example Request

https://delphi-stats-api.herokuapp.com/liquidity

#### Example Response

```
{
  "0x051e3a47724740d47042edc71c0ae81a35fdede9": 100015.03825086306,
  "0x08ddb58d31c08242cd444bb5b43f7d2c6bca0396": 289805.6282660929,
  "0x7967ada2a32a633d5c055e2e075a83023b632b4e": 856831.0900003031,
  "0x91d7b9a8d2314110d4018c88dbfdcf5e2ba4772e": 1614597.080648649,
  "0x9984d588ef2112894a0513663ba815310d383e3c": 320301.016744,
  "0xbed50f08b8e68293bd7db742c4207f2f6e520cd2": 73380.69830087328,
  "0xeae1a8206f68a7ef629e85fc69e82cfd36e83ba4": 283849.8705576786
}
```

### GET /rewards

This gets the list of weekly rewards of each token. It is calculated by looking at all the rewardDistribution events for the pool, and summing all the rewards from the past week

#### Example Request

https://delphi-stats-api.herokuapp.com/rewards

#### Example Response

```
{
  "0x051e3a47724740d47042edc71c0ae81a35fdede9": {
    "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": 17547.685185185186,
    "0x94d863173ee77439e4292284ff13fad54b3ba182": 2467.204537037037
  },
  "0x08ddb58d31c08242cd444bb5b43f7d2c6bca0396": {
    "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": 17533.16798941799,
    "0x94d863173ee77439e4292284ff13fad54b3ba182": 1233.4583680555556,
    "0xc00e94cb662c3520282e6f5717214004a7f26888": 3.2781489124141463
  },
  "0x7967ada2a32a633d5c055e2e075a83023b632b4e": {
    "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": 245397.2222222222,
    "0x94d863173ee77439e4292284ff13fad54b3ba182": 34508.984375,
    "0xd533a949740bb3306d119cc777fa900ba034cd52": 3317.2082757140784
  },
  "0x91d7b9a8d2314110d4018c88dbfdcf5e2ba4772e": {
    "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": 245430.09259259258,
    "0x94d863173ee77439e4292284ff13fad54b3ba182": 34513.606770833336,
    "0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f": 84.34901794077209,
    "0xd533a949740bb3306d119cc777fa900ba034cd52": 5421.500114496502
  },
  "0x9984d588ef2112894a0513663ba815310d383e3c": {
    "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": 17540.74074074074,
    "0x94d863173ee77439e4292284ff13fad54b3ba182": 1233.991111111111,
    "0xc00e94cb662c3520282e6f5717214004a7f26888": 1.7503685739594372
  },
  "0xbed50f08b8e68293bd7db742c4207f2f6e520cd2": {
    "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": 17547.08994708995,
    "0x94d863173ee77439e4292284ff13fad54b3ba182": 2467.1208465608465
  },
  "0xeae1a8206f68a7ef629e85fc69e82cfd36e83ba4": {
    "0xd533a949740bb3306d119cc777fa900ba034cd52": 2144.7399084080826
  }
}
```

### GET /stats

This gets detailed stats about yearly total returns of each token.

1. First the weekly rewards are identified for each pool.
2. Next we multiply this by 52.1429 (weeks in a year)
3. The price for each of these reward tokens from CoinGecko API is calculated
4. Yearly income in USD from reward tokens is calculated (price \* amount)
5. We calculate this yearly income/liquidity of the pool, to calculate the %APY of this reward token
6. This is repeated for each reward token
7. Capital Gains = Rewards APY of each pool is then calculated
8. All these APY %, are summed and represented under the Total field in apy

#### Example Request

https://delphi-stats-api.herokuapp.com/stats

#### Example Response

```
{
  "0x051e3a47724740d47042edc71c0ae81a35fdede9": {
    "Liquidity": 100015.03825086306,
    "Name": "Delphi Aave BUSD",
    "apy": {
      "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": {
        "apy": 14.739828308035648,
        "price": 0.01611175,
        "yearly_amount": 914987.1938425926
      },
      "0x94d863173ee77439e4292284ff13fad54b3ba182": {
        "apy": 144.06319880354332,
        "price": 1.12,
        "yearly_amount": 128647.19945426851
      },
      "CapitalGains": 3.562414425476534,
      "Total": 162.3654415370555
    }
  },
  "0x08ddb58d31c08242cd444bb5b43f7d2c6bca0396": {
    "Liquidity": 289805.6282660929,
    "Name": "Delphi Compound DAI",
    "apy": {
      "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": {
        "apy": 5.082664859987909,
        "price": 0.01611175,
        "yearly_amount": 914230.2251554233
      },
      "0x94d863173ee77439e4292284ff13fad54b3ba182": {
        "apy": 24.855979620349583,
        "price": 1.12,
        "yearly_amount": 64316.09633968403
      },
      "0xc00e94cb662c3520282e6f5717214004a7f26888": {
        "apy": 9.01003946746893,
        "price": 152.76,
        "yearly_amount": 170.93219092511958
      },
      "CapitalGains": 4.7646549904520255,
      "Total": 43.713338938258445
    }
  },
  "0x7967ada2a32a633d5c055e2e075a83023b632b4e": {
    "Liquidity": 856831.0900003031,
    "Name": "Delphi Curve yPool",
    "apy": {
      "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": {
        "apy": 24.060925137845384,
        "price": 0.01611175,
        "yearly_amount": 12795722.81861111
      },
      "0x94d863173ee77439e4292284ff13fad54b3ba182": {
        "apy": 235.20695822680023,
        "price": 1.12,
        "yearly_amount": 1799398.5213671874
      },
      "0xd533a949740bb3306d119cc777fa900ba034cd52": {
        "apy": 26.64689657883037,
        "price": 1.32,
        "yearly_amount": 172968.85939973162
      },
      "CapitalGains": 21.992668362920426,
      "Total": 307.9074483063964
    }
  },
  "0x91d7b9a8d2314110d4018c88dbfdcf5e2ba4772e": {
    "Liquidity": 1614597.080648649,
    "Name": "Delphi Curve sUSD",
    "apy": {
      "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": {
        "apy": 12.770313066434978,
        "price": 0.01611175,
        "yearly_amount": 12797436.775046295
      },
      "0x94d863173ee77439e4292284ff13fad54b3ba182": {
        "apy": 124.83586872707868,
        "price": 1.12,
        "yearly_amount": 1799639.5464908856
      },
      "0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f": {
        "apy": 1.2012949143728626,
        "price": 4.41,
        "yearly_amount": 4398.202407583884
      },
      "0xd533a949740bb3306d119cc777fa900ba034cd52": {
        "apy": 23.111302445358433,
        "price": 1.32,
        "yearly_amount": 282692.73832017963
      },
      "CapitalGains": 22.679395295363236,
      "Total": 184.59817444860818
    }
  },
  "0x9984d588ef2112894a0513663ba815310d383e3c": {
    "Liquidity": 320301.016744,
    "Name": "Delphi Compound USDC",
    "apy": {
      "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": {
        "apy": 4.6007380649536636,
        "price": 0.01611175,
        "yearly_amount": 914625.0903703703
      },
      "0x94d863173ee77439e4292284ff13fad54b3ba182": {
        "apy": 22.499191808079757,
        "price": 1.12,
        "yearly_amount": 64343.87510755555
      },
      "0xc00e94cb662c3520282e6f5717214004a7f26888": {
        "apy": 4.352873250012655,
        "price": 152.76,
        "yearly_amount": 91.26929351510954
      },
      "CapitalGains": 2.628552914099433,
      "Total": 34.081356037145504
    }
  },
  "0xbed50f08b8e68293bd7db742c4207f2f6e520cd2": {
    "Liquidity": 73380.69830087328,
    "Name": "Delphi Aave sUSD",
    "apy": {
      "0x8ab7404063ec4dbcfd4598215992dc3f8ec853d7": {
        "apy": 20.089131330515517,
        "price": 0.01611175,
        "yearly_amount": 914956.1564021165
      },
      "0x94d863173ee77439e4292284ff13fad54b3ba182": {
        "apy": 196.34587731804052,
        "price": 1.12,
        "yearly_amount": 128642.83559013756
      },
      "CapitalGains": 11.298503076965972,
      "Total": 227.73351172552202
    }
  },
  "0xeae1a8206f68a7ef629e85fc69e82cfd36e83ba4": {
    "Liquidity": 283849.8705576786,
    "Name": "Delphi Curve BUSD",
    "apy": {
      "0xd533a949740bb3306d119cc777fa900ba034cd52": {
        "apy": 52.0061908157811,
        "price": 1.32,
        "yearly_amount": 111832.9585701318
      },
      "CapitalGains": 31.587393071579612,
      "Total": 83.59358388736072
    }
  }
}

```
