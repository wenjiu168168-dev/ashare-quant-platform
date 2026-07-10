# A-Share Quant Research Platform

A-Share Quant Research Platform 是面向中国 A 股市场的量化研究、回测评估与交易决策支持平台。项目优先追求数据可追溯、研究可复现、风险可解释和工程可维护，而不是追求短期回测收益最大化。

## 项目目标

- 建立可持续维护的 A 股量化研究工程体系。
- 支持后续接入市场数据、股票池、因子、信号、策略、组合、风险、回测、评估和报告模块。
- 根据每日市场数据生成候选股票、参考买入区间、失效条件、止损位、止盈规则、仓位建议和卖出条件等研究型输出。
- 为每个信号提供清晰、可解释、可验证的依据。
- 优先控制回撤、流动性风险、过度拟合、未来函数、幸存者偏差和数据泄漏。

## 非目标

- 第一版不接入真实券商交易。
- 第一版不执行真实订单。
- 第一版不生成任何实盘买卖指令。
- 当前阶段不接入 Tushare、AkShare 或任何真实数据源。
- 当前阶段不要求 API Token。
- 当前阶段不实现完整交易策略和复杂前端。

## 重要风险声明

本项目仅用于量化研究、回测评估和交易决策支持，不构成投资建议。系统不能保证盈利，不能承诺稳定收益。任何回测结果都不等于未来收益，历史表现不代表未来表现。使用者需要自行承担市场风险、流动性风险、模型风险、数据风险和执行风险。

## 目标市场范围

- 上海证券交易所
- 深圳证券交易所
- 北京证券交易所
- 主板
- 创业板
- 科创板
- ETF（后续阶段）

可转债暂不纳入第一版。

## 第一版技术栈

- Python 3.11
- uv（优先）或 Poetry
- pandas、numpy、polars
- pydantic
- SQLAlchemy
- DuckDB
- PostgreSQL 预留支持
- Tushare 首选数据源（后续阶段）
- AkShare 备用公开数据源（后续阶段）
- pytest、ruff、mypy、pre-commit
- GitHub Actions
- Docker
- FastAPI
- Dashboard 方案后续在 Streamlit 与 React 间选择

## 当前阶段状态

当前仓库处于 Phase 0：项目规范和工程骨架阶段。本阶段只建立项目规划文档、风险原则、数据政策、完成定义和建议目录结构，不实现完整业务逻辑。

## 建议阅读顺序

1. `docs/PROJECT_CHARTER.md`
2. `docs/RISK_PRINCIPLES.md`
3. `docs/DATA_POLICY.md`
4. `docs/ARCHITECTURE.md`
5. `docs/ROADMAP.md`
6. `docs/DEFINITION_OF_DONE.md`
7. `AGENTS.md`
