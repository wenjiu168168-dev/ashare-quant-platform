# Data Provider Interface

## 职责

Provider 层负责为外部或内部数据源建立稳定边界。它定义数据源身份、能力声明、健康检查、生命周期管理、注册与获取机制，以及统一异常类型。后续 Tushare、AkShare、JoinQuant、Wind 等真实数据源适配器必须实现该边界。

## 非职责

Provider 层当前不负责：

- 连接真实数据源。
- 保存 API Token 或密钥。
- 下载真实行情、财务或指数数据。
- 定义完整 `DailyBar`、`MinuteBar`、`StockBasic` 等行情模型。
- 创建数据库表、DuckDB 存储、缓存系统或交易日历实现。
- 生成股票池、因子、信号、策略、回测结果、买卖建议或交易订单。

## 为什么策略和回测不能直接调用第三方 API

策略、回测和报告如果直接调用第三方 API，会破坏可复现性和审计能力，也容易引入未来函数、数据泄漏、字段口径漂移、授权边界不清和测试不可控等问题。所有外部数据必须先经过 Provider 层、数据质量检查、元数据记录和时间语义校验，才能进入后续研究链路。

## 如何实现新的 Provider

新的 Provider 应：

1. 继承 `BaseDataProvider`。
2. 提供稳定唯一的 `provider_id`，例如 `tushare`、`akshare` 或 `mock`。
3. 提供人类可读的 `display_name`。
4. 返回不可变的 `frozenset[ProviderCapability]`。
5. 实现 `health_check()` 并返回 `ProviderHealth`。
6. 如持有文件、连接或会话资源，重写 `close()` 释放资源。
7. 不在构造函数中隐式联网或下载数据。
8. 不在代码中写入 API Token、密码或其他密钥。

## Capability 的用途

`ProviderCapability` 是稳定、可序列化、类型安全的能力枚举，用于判断 Provider 是否支持某类数据边界。第一版包括：

- `STOCK_BASIC`
- `TRADING_CALENDAR`
- `DAILY_BAR`
- `MINUTE_BAR`
- `CORPORATE_ACTION`
- `FINANCIAL_STATEMENT`
- `INDEX_DAILY`
- `ETF_DAILY`

调用方应使用 `provider.supports(capability)` 进行集合判断，不得使用自由字符串替代能力枚举。

## Registry 的用途

`ProviderRegistry` 用于在应用或测试上下文中注册、获取、注销和列出 Provider 实例。Registry 是可实例化对象，便于测试和依赖注入。第一版没有提供全局单例，避免测试污染和隐式共享状态。

## 异常处理规则

Provider 相关异常均继承 `DataProviderError`，而 `DataProviderError` 继承项目统一异常基类 `AShareQuantError`。调用方不得吞掉原始异常；需要保留根因时应使用异常链：

```python
raise ProviderConfigurationError(provider_id, "invalid token source") from exc
```

## 生命周期和 close 规则

所有 Provider 都支持上下文管理器：

```python
with provider:
    ...
```

退出上下文时会调用 `close()`。无外部资源的 Provider 可以使用默认 `close()`；持有文件、网络会话或数据库连接的 Provider 必须重写 `close()`。

## 线程安全限制

`ProviderRegistry` 第一版不保证线程安全。多线程或异步运行环境后续应增加同步边界、不可变注册表快照或应用生命周期管理。

## 后续真实数据源接入

后续接入真实数据源时，应先完成：

1. Token 管理和授权边界设计。
2. 数据源字段、更新时间、授权限制和元数据记录。
3. 数据质量检查和时间语义校验。
4. 小样本、无网络单元测试与可控集成测试。

## 本任务声明

Task-2.1.1 仅建立接口边界和内存测试实现。本任务未接入任何真实数据源、未使用 API Token、未下载股票数据、未连接交易接口、未生成股票代码或买卖建议。
