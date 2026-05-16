# Technical Domain Routing

## Purpose
Arthur routes PRDs by technical domain, not just by market.

A request about a trading market is not enough to choose the developer.
Arthur must identify the actual implementation target.

## Routing examples

| Request | Route |
|---|---|
| TradingView indicator | Arthur → Felix → Ben |
| TradingView Pine Script strategy | Arthur → Felix → Ben |
| Quantower automation script | Arthur → Nathan → Grant |
| Quantower C# trading algorithm | Arthur → Nathan → Grant |
| Backend API / service / Rust / Node / Python | Arthur → Marcus → Jack |
| Security-sensitive backend change | Arthur → Marcus → Safiya / Cody as needed |
| DevOps / infra | Arthur → Viktor / Theo |
| Mobile | Arthur → Dominic / Ellie / Dante |
| Frontend UI | Arthur → Sonia / Leo |

## Hard rule
Arthur must route to the best technical specialist based on the PRD target:
- platform
- language
- runtime
- execution environment
- safety/risk impact
- testing requirements
