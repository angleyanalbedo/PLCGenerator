# Changelog

本文件记录项目的重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循
[Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

当前版本尚无已发布变更。

## [0.1.0] - 2026-09-19

### Added

- 发布项目初始版本。
- 新增蒸馏引擎（Distillation Engine）：
  - 基于 Evol-Instruct 自动将基础 ST 编程任务进化为复杂任务。
  - 提供快速语法校验、Matiec 编译校验和 AI 逻辑审查三级校验流水线。
  - 支持校验失败自动重试，并可配置最大重试次数。
  - 支持断点续传，可从中断处恢复蒸馏过程。
- 新增双路 GraphRAG 检索系统：
  - 支持本地向量数据库中的精确代码库检索。
  - 支持 IEC 61131-3 标准文档的全局手册库检索。
  - 支持沿 `calls` 边遍历图谱，自动补全被调用函数定义。
- 新增基于 ANTLR4 的 AST 构建引擎：
  - 支持完整 ST 语法解析并构建结构化抽象语法树。
  - 支持 30 多种 AST 节点类型，包括 `Program`、`FunctionBlock`、`Function`、`Method`、`Case`、`For` 和 `While` 等。
  - 将结构操作与校验判定解耦。
- 新增 ST → FBD → LD 跨语言转换器：
  - 支持 ST 源码转换为 FBD，再转换为 LD。
  - 支持输出符合 IEC 61131-10 的 XML 文件。
- 集成 Matiec 编译器，用于验证 ST 代码并记录编译通过率和日志。
- 新增数据增强器，支持逻辑等价变换、变量重命名、结构变换和注释生成。
- 新增 Golden Memory 系统，自动收录校验通过的代码作为后续生成参考样本。
- 新增在线 DPO 数据自动构造：利用失败重试成功的过程自动配对 `Chosen` 和 `Rejected` 样本。
- 新增 AI 逻辑审查闭环，对编译通过但可能存在逻辑问题的代码进行二次审查，并将结果反馈至蒸馏流程。
- 新增全链路异步并发架构，支持配置并发数上限。
- 新增版权声明，明确项目为个人独立开发，与实验室无关。

### Infrastructure

- 建立 GitHub 仓库。
- 完成 GPG 签名 commit 配置。
- 添加项目版权声明文件。

## 版本说明

- **[Unreleased]**：当前开发中、尚未发布的变更。
- **[0.1.0]**：初始功能版本，包含蒸馏引擎、GraphRAG、AST 引擎和跨语言转换等核心模块。

发布新版本时，将 `[Unreleased]` 下已完成的变更移入对应版本号和日期的章节，并在顶部保留新的空白 `[Unreleased]` 章节。
