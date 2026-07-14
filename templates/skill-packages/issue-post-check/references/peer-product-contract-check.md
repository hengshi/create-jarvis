# 同类产品契约检查

仅当 disposition 明确依赖当前产品外部的行业/同类契约，且授权 source 可访问时使用。外部做法只能提供上下文，不能单独证明 by-design 或 feature gap。

## 何时不先读此

- 有明确的异常或回归证据；先走 defect / duplicate 路由
- 基本事实缺失；先收集 live 证据

## 目标

把外部契约参考从临时意见升级为可追溯上下文。最终 disposition 由 {{PRODUCT_IDENTITY}} 已确认产品范围和客户证据决定。

## 触发条件

claim 实质是契约争议而非程序错误——reporter 认为当前行为违反某种合理预期，而该预期部分来源于外部参照。

## 方法

1. 写出待验证的外部契约 claim：不带方案偏差的一句话。
2. 从授权 source 找直接相关的一手公开或授权材料。
3. 比较外部材料的适用上下文与 {{PRODUCT_IDENTITY}} 已确认契约：
   - overlap：一致之处
   - delta：不同之处及是否有明确设计理由
4. 外部做法提供上下文，不单独构成 by-design 或 feature gap 结论。
5. 最终 disposition 回到 {{PRODUCT_IDENTITY}} 已确认产品范围和客户证据。

## 完成条件

- 只读取与外部契约 claim 直接相关、且授权可访问的来源；证据足以说明上下文或授权范围耗尽时停止。
- 比较维度来自 claim 和来源本身，不预设产品形态或行业分类。
- 最终判断主体始终是 {{PRODUCT_IDENTITY}} 的产品定位和已确认边界。
