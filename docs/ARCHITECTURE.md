# Architecture

## 架构目标

平台采用分层、模块化、配置驱动的架构。核心目标是将数据接入、数据质量、股票池、因子、信号、策略、组合、风控、回测、评估和报告解耦，确保每个模块可以独立测试、替换和审计。

## 建议目录结构

```text
src/
  ashare_quant/
    config/       # 配置模型、配置加载、环境变量读取
    data/         # 数据提供者接口、数据源适配、数据清洗、数据质量检查、存储接口
    universe/     # 股票池、指数成分、上市状态、ST/退市过滤
    factors/      # 因子计算、因子验证、因子元数据
    signals/      # 信号生成、信号解释、信号失效条件
    strategies/   # 策略组合逻辑，不直接执行真实交易
    portfolio/    # 组合构建、调仓、仓位约束
    risk/         # 风险规则、止损止盈、敞口和流动性约束
    execution/    # 模拟执行、成交假设；第一版不连接真实券商
    backtest/     # 回测引擎、撮合假设、交易成本和 T+1 约束
    evaluation/   # 绩效评估、基准对比、归因和稳健性分析
    reporting/    # 每日报告、实验报告、风险提示输出
    api/          # FastAPI 服务接口
    dashboard/    # Dashboard 预留，Streamlit 或 React 后续决策
    utils/        # 通用工具，禁止放置业务核心逻辑

tests/
  unit/
  integration/
  regression/

configs/
  data/
  strategy/
  risk/
  backtest/

scripts/
notebooks/
docs/
data/
  raw/
  interim/
  processed/
  features/
reports/
experiments/
```

当前阶段仅创建规划文档和必要空目录，不完整实现上述模块。

## 数据流

1. 数据提供者接口统一声明数据源身份、能力、健康状态和生命周期。
2. 数据源适配器通过 Provider 边界拉取原始数据。
3. 原始数据进入 `data/raw/` 或数据库原始层。
4. 数据质量检查记录缺失、异常、复权、交易状态和授权信息。
5. 清洗后数据进入 `data/interim/`、`data/processed/` 或 DuckDB/PostgreSQL。
6. 因子模块只读取在信号生成时间之前可获得的数据。
7. 信号模块生成可解释信号，并记录信号生成时间和最早可成交时间。
8. 策略和组合模块结合风险约束生成研究型仓位建议。
9. 回测模块使用真实交易约束、交易费用、滑点和冲击成本评估。
10. 评估模块输出基准对比、样本内、样本外和滚动验证结果。
11. 报告模块输出候选股票、风险提示和信号解释。

## 时间语义

系统必须严格区分：

- 数据自然日期。
- 交易日。
- 数据发布时间。
- 数据入库时间。
- 信号生成时间。
- 最早可成交时间。
- 回测撮合时间。

任何不能证明在当时可获得的数据，都不得用于当时的信号、回测或决策支持。

## 配置原则

- 所有参数必须进入 `configs/` 或受版本控制的配置模型。
- 使用 `pydantic-settings` 进行统一配置读取和校验。
- 禁止在业务代码中散落硬编码参数。
- 禁止在业务模块中散落调用 `os.getenv()`；需要新增配置时必须扩展统一配置模型。
- 敏感信息不得进入配置文件和代码仓库。
- 每次实验必须记录配置快照、代码版本和数据版本。

## 存储规划

- 本地研究优先使用 DuckDB。
- 后续生产化或多人协作场景预留 PostgreSQL。
- 文件层按 raw、interim、processed、features 分层。
- 实验产出写入 `experiments/`，报告写入 `reports/`。

## 测试策略

- `tests/unit/`：核心函数、配置、日志、异常、时间对齐、交易约束和成本计算。
- `tests/integration/`：数据流、存储接口、因子到信号链路。
- `tests/regression/`：固定小样本回测和报告输出，防止行为漂移。
