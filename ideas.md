# 设计思路

目前支持超大 Android 应用的重构代码分析，重构目标是将百万级代码代码拆分成多个module，满足如下要求：
1. 共用的基础功能提取成 aar，组成平台
2. 提取一个底座『壳』应用
3. 业务模块变成可以独立编译的业务 bundle
4. 『横向和纵向』依赖关系清晰

当前的情况是，应用虽然划分了 module，但 module 之前的依赖关系没有约束，形成了大泥球。

第一步先要将，平台、『壳』应用、业务 bundle 之间的横向边界识别出来，并选择一个业务领域将其和其他业务领域的纵向边界识别出来。

本工具的目标是辅助开发对代码进行分析
1. 通过规则将现有的依赖关系进行分类（依赖第三方、其他模块、Android 等等），分类规则可以自定义（例如可以区分哪些依赖是指向平台层的）。
2. 通过规则识别处不正确的依赖关系，包括依赖指向不对、依赖不应存在、循环依赖，判断规则在阅读代码过程中进行总结。
3. 通过可视化方式将结果进行记录和呈现。

最终通过工具生成的清单或者 UML 类图，将依赖坏味道作为重构改进点的输入。

工具限制：
1. 需要整个工程能够在 AndroidStudio 编译通过（能生成 index）
2. 需要使用 AndroidStduio 的 Dependency Analysis 功能导出原始依赖关系（raw/test_deps.xml）作为工具的输入

工具执行流程如下

1. 解析 raw/test_deps.xml，解析成 CLS 对象（类）及其依赖（dependencies 成员，DEP 对象的 list）
   > 解析主要依据是 path 属性的值，用正则表达式解析处该类所属 module、package 及其名称
   > AndroidStudio 导出的 xml 中没有具体的依赖关系（如继承、聚合等等），但作为重构分析辅助已经足够。
   （TODO）支持其他格式的依赖关系文件解析

2. 用正则表达式对 CLS 对象的成员 dependencies 进行分类
   > 正则表达式需要根据 path 的特征编写
   > 正则表达式有限制（严格的在前）
   > 分类和对应的正则表达式可以进行扩展，阅读代码时发现的规律可以及时增加

3. （TODO）用正则表达式标记 CLS 对象 dependencies 成员中不正常的 DEP 对象
    > 可以参考 AndroidStduio  Dependency Analysis 的 Illegal Rule规则
    > 可以参考 ArchUnit 测试用例描述

4. 生成可视化结果
   1.1. Console 输出（已支持）
   1.2. CSV 导出（已支持，每个 module 一个文件，每个 CLS 一行）
   1.3. (TODO)PlantUML导出（TBD: 每个 module 一个 puml 文件，包含 package 和 class，依赖问题用文字描述，用颜色区分）
      > puml 可以作为新架构设计的输入进行修改


  

```mermaid
graph TD
    A[Start] --> B{Is it?};
    B -- Yes --> C[OK];
    C --> D[Rethink];
    D --> B;
    B -- No ----> E[End];
```
|   |   |
|---|---|
|   |   |

