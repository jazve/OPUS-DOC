

# **伪代码在AI工作流编排中的潜力与挑战：取代复杂外部工具的可能性**

## **执行摘要**

本报告探讨了伪代码，特别是结合Markdown启发式语法时，作为定义和编排AI模型执行流程及外部工具交互的轻量级而强大机制的变革潜力。伪代码历来是面向人类的设计辅助工具，但正日益成为复杂传统工作流工具的可行替代方案，为大型语言模型（LLMs）提供了更高的清晰度、简洁性和适应性。尽管标准化、解析鲁棒性和安全性方面的重大挑战依然存在，但将伪代码集成到AI系统中预示着LLM性能的提升、开发流程的简化以及高级人机协作的实现。未来的发展方向指向自动化伪代码生成、自优化AI以及人类角色向高层设计和监督的重新定义。

## **1\. 引言：AI工作流编排的演变格局**

随着大型语言模型（LLMs）能力的飞速发展，它们已被整合到日益复杂的应用中，涵盖了从多跳检索和问答到自主代理工作流等多个领域 1。这种复杂性的增加对操作序列、数据流以及与外部系统的交互提出了更高的要求，从而凸显了对强大且灵活的工作流管理机制的需求。传统AI模型通常擅长执行单一任务，但代理AI系统则被设计用于多步骤规划、推理、行动和随时间推移的适应 2。这种AI能力的基本转变要求更复杂但同时又更灵活的工作流编排解决方案。

当前，现有的LLM处理复杂任务的方法，例如图计算问题，往往难以理解复杂的图结构，并产生高昂的推理成本，特别是对于大规模图而言 3。这种低效率的根源在于，整个图结构需要被序列化并整合到提示中，导致提示过长，严重影响推理效率 4。此外，传统的硬编码对话管理器或僵化的工作流工具缺乏AI应用动态演变所需的内在灵活性和适应性 5。因此，业界迫切需要能够通过人类可读指令（而非复杂的低级编程代码）声明性地定义控制流的机制 5。

在此背景下，伪代码提供了一个有前景的方向。伪代码本质上是对算法的人类可读、独立于语言的描述 6。其核心目的是专注于程序的逻辑和流程，抽象掉任何特定编程语言的精确语法。这使其成为抽象定义复杂AI工作流的固有吸引力候选者。通过策略性地整合结构化元素，并可能借鉴广泛采用的Markdown语法，可以有效地弥合非正式人类理解与精确机器可解释性之间的鸿沟。这种混合方法有望使LLMs充当高度灵活和高效的“工作流解释器” 5。

值得注意的是，当前面临的挑战不仅仅是复杂性，还包括僵化和成本。现有工具之所以被认为是“复杂”的，部分原因在于它们是“传统的硬编码对话管理器”，这暗示了其缺乏灵活性和固有的僵化性 5。此外，当LLMs处理图等结构化数据时，需要将整个图结构序列化并整合到提示中，导致提示长度过长，从而产生“高昂的计算成本” 4。因此，伪代码的价值主张超越了仅仅简化人类对复杂逻辑的理解。它还提供了显著降低计算复杂性（通过更短、更专注、更节省token的提示）和大幅提高适应性（通过实现声明性、人类可读的控制流定义）的潜力。这预示着AI工作流管理将从命令式、僵化的编排向更声明式、灵活和成本效益更高的方法转变。

## **2\. 伪代码：AI工作流定义的基础**

### **伪代码的定义与核心特征**

伪代码是对算法或程序的一种非正式、高级描述，它有意地将自然语言与常见的编程约定相结合 6。其设计明确省略了机器直接实现所需的微小细节，优先考虑人类可读性以及对底层逻辑和流程的清晰阐述 7。

伪代码的关键特征包括其固有的语言独立性、高可读性、描述性以及简化的结构，它刻意避免了任何特定编程语言的严格语法规则 7。伪代码通常采用基本的编程构造，例如

SEQUENCE（顺序）、CASE（选择）、WHILE（循环）、REPEAT-UNTIL（重复直到）、FOR（循环）和IF-THEN-ELSE（条件判断），并且还可以表示函数调用 6。伪代码的核心目的是以简洁的方式表达一个想法，使熟悉该符号（其规则可以根据作者的意愿严格或宽松）的人能够快速掌握概念，而无需纠结于任何特定语言所施加的技术细节 12。

### **伪代码在AI提示工程中的优势**

伪代码在AI提示工程中展现出多重优势，显著提升了大型语言模型（LLMs）的性能和应用效率。

首先，伪代码本质上提供了比自然语言更清晰、更精确的提示风格，从而减少了自然语言固有的歧义 13。这种增强的清晰度直接有助于提高LLM的性能 13。

其次，实证研究表明，使用伪代码指令对预训练LLMs可以带来显著的性能提升。这些改进包括分类任务的F1分数平均绝对增加7-16个百分点，以及所有任务的ROUGE-L总分相对提高12-38% 13。这些收益归因于伪代码中嵌入的结构线索、代码注释和文档字符串 13。

第三，伪代码可以非常紧凑 17，这在token受限的LLM提示背景下是一个显著优势。这种简洁性直接转化为推理成本的降低 3。例如，PIE（伪代码注入魔法）框架实现了更低的LLM调用成本，因为其提示长度由于伪代码注入而保持常数（O(1)），这与某些将序列化图结构纳入提示的方法不同，后者会导致提示长度取决于边数（O(|E|)） 3。

第四，伪代码在指导复杂推理方面非常有效。它能引导LLMs生成高效代码，并防止它们在面对NP完全问题时退回到效率较低的暴力算法 3。它还可以帮助LLMs将复杂问题分解为逐步推理过程，其功能类似于思维链（CoT）提示 18。

最后，伪代码的语言无关性使其独立于特定编程语言的语法，允许开发人员专注于算法逻辑，从而在设计阶段提供更大的灵活性和更便捷的沟通 19。这一特性还使LLMs能够从单一、统一的伪代码表示生成各种目标语言的功能代码 20。

伪代码能够充当LLMs的“结构先验”。研究一致表明，伪代码能提高LLM的性能 14。这种改进与伪代码比自然语言“歧义更少”、“更简洁”和“更清晰”有关 13。至关重要的是，消融研究表明，伪代码中的“结构线索”是这种增强效果的重要促成因素 13。LLMs受益于结构化输入，而伪代码提供了这种结构。对这种效果更深层次的理解是，LLMs在大量数据上进行了训练，其中包括大量的实际代码 13。代码本身具有强大且一致的结构（例如，函数、循环、条件块、缩进）。伪代码，即使在其非正式变体中，也模仿了这种基本的结构组织 6。因此，伪代码提供了一个强大的“结构先验”或“模板”，与LLM对计算逻辑的预训练理解产生共鸣。这使得模型能够更有效地解析人类意图并生成正确、高效的输出。这超越了简单的语言清晰度；它利用了模型对程序结构的内部表示，表明LLMs不仅是自然语言的复杂模式匹配器，也是代码中固有的逻辑和结构模式的匹配器。

**表1：伪代码与自然语言提示在LLM应用中的比较**

| 标准 | 伪代码 | 自然语言 |
| :---- | :---- | :---- |
| **歧义性** | 低（结构化逻辑） | 高（人类语言固有） |
| **简洁性** | 高（紧凑表示） | 低（可能冗长） |
| **LLM性能（准确性/F1/ROUGE）** | 更高（经验证，提升显著） 13 | 较低（相比伪代码提示） |
| **复杂逻辑引导** | 强（多步骤推理，高效算法） 3 | 弱（常需CoT或Few-shot等额外技术） |
| **Token效率** | 高（O(1)提示长度，例如PIE） 3 | 低（可能导致长提示） |
| **人类可读性（目标受众）** | 高（技术用户/程序员） | 高（普通大众） |
| **机器可解释性** | 中高（特别是结构化语法） | 低中 |
| **主要用例** | 算法设计、复杂任务分解、代理控制、代码生成 | 通用查询、对话式AI、创意文本生成 |

## **3\. 伪代码作为复杂工作流工具的替代方案**

### **3.1. 使用伪代码定义模型执行流程**

伪代码提供了一种清晰且结构化的方式来指定顺序、条件（IF-THEN-ELSE、CASE）和迭代（WHILE、FOR、REPEAT-UNTIL）步骤，有效地构成了AI模型执行的逻辑蓝图 6。这种能力对于将复杂问题分解为更小、更易于管理的步骤至关重要 8。

伪代码可以指导多步骤推理过程，其功能类似于思维链（CoT）提示，其中伪代码明确充当结构化中间步骤 18。例如，“Self-Pseudo”基线通过首先定义问题需求，然后生成伪代码以在多阶段过程中指导最终代码创建来证明了这一点 18。PIE框架通过将复杂的图问题解决过程分解为不同的阶段（问题理解、提示设计（关键是伪代码注入）以及随后的代码生成和执行）来例证了这一点。伪代码有效地指导LLM生成高效的代码解决方案 3。

伪代码能够使LLMs实现“程序化思维”。伪代码有助于LLMs进行多步骤推理 18 并生成高效代码 3。这超越了简单的文本生成。当LLM处理伪代码时，它不仅仅是在执行语言任务；它是在解释一个计算计划。这种解释使LLM能够进行一种“程序化思维”或“算法推理”。这种“程序化思维”使LLMs能够系统地分解和解决复杂问题，超越了其可能优先考虑看似合理而非精确计算的概率自回归解码方式 4。它为LLM的内部“思考过程”提供了一个结构化的脚手架，使其能够处理需要清晰逻辑流的复杂多步骤AI任务。

### **3.2. 编排工具调用和外部交互**

伪代码可以明确定义外部工具的调用、参数的传递以及结果的处理 25。例如，一个AI代理核心循环的伪代码示例展示了这一点：

subtask \= planner.plan(goal, memory)（子任务 \= 规划器.规划(目标, 记忆)），result \= executor.execute(subtask)（结果 \= 执行器.执行(子任务)），以及memory.store(subtask, result)（记忆.存储(子任务, 结果)） 2。

工具通常在提示或可访问的tool\_map中定义，并附有清晰的描述和预期参数，使LLM能够智能地选择和调用适当的工具 25。伪代码示例中的

parse\_action和parse\_action\_input等函数说明了如何从LLM响应中提取工具名称及其相应参数以进行后续执行 25。这种能力使LLMs能够与各种外部系统动态交互，包括API、文件系统、编译器、解释器、测试套件和数据库 2。LangChain等框架通过模块化地链接提示、工具、API和内存组件进一步促进了这一点 27。

伪代码有助于实现AI的“声明式代理架构”。伪代码明确用于定义AI代理中的工具调用和执行流程 2。代理AI系统的特点是规划、记忆、工具使用和反思 2。如果伪代码定义了这些步骤，这意味着人类设计者可以在高层、抽象的层面声明性地指定代理的行为。这种更深层次的理解在于，伪代码定义了代理迭代循环的逻辑（例如，

while not goal\_achieved: subtask \= planner.plan(...)）。这从根本上将代理的“编程”从低级、命令式代码转变为高级、人类可读的伪代码指令。这构成了一种“声明式”方法，因为人类陈述了代理应该完成“什么”以及其高层流程“如何”进行（用伪代码），而底层的LLM/解释器则负责找出精确的执行“方式”。这种分工使得领域专家能够使用自然语言或伪代码设计复杂的对话工作流，而软件工程师则可以专注于开发强大的核心API实现 28。这种“声明式代理架构”简化了复杂AI系统的开发和部署，使其对非程序员更易于访问，并显著加速了迭代周期。这种方法有望通过提供更灵活、更以人为本的设计范式来取代对定制的、复杂且僵化的工作流工具的需求。

### **3.3. 利用Markdown类语法实现结构化工作流**

用户查询明确提到了Markdown，研究也证实了其效用。Markdown可以有效地用于划分部分、定义变量和构建伪代码中的控制流，从而增强人类可读性和机器可解释性 29。CodeWeaver等工具展示了Markdown的实际应用，通过将整个代码库编织成结构化的Markdown文档。这简化了代码库导航、文档编写以及与AI/ML代码分析工具的集成 30。

InstructPipe是一个用于生成AI管道的研究原型，它使用一种“简洁的代码格式”（伪代码）来定义节点选择和连接。这种伪代码随后被编译成JSON格式以供执行。至关重要的是，这种伪代码表示具有高度的token效率，能够显著压缩复杂的管道定义（例如，从2.8k个token压缩到仅123个token） 31。Obsidian插件的存在，能够将LaTeX风格的伪代码渲染到Markdown代码块中，进一步突出了将伪代码形式化以实现视觉吸引力和全面文档的实用且专业的方法 29。

Markdown增强的伪代码可以充当AI工作流的“中间表示”。Markdown用于结构化伪代码 29。伪代码反过来又被证明是token高效的，并且可以编译成JSON等可执行格式 31。结构化伪代码，特别是结合Markdown时，可以改善LLM处理，并可转换为机器可执行格式。对这种能力更深层次的理解是，将复杂、冗长的信息（如管道的JSON表示）压缩成高度token高效的伪代码格式，然后由LLM或解释器进行“重新编译”（解释或转换），这表明这种结构化伪代码在AI工作流中充当了“中间表示”。这种中间表示针对双重目的进行了优化：人类理解和设计（由于其可读性和结构化特性）以及高效的LLM处理（由于其简洁性和清晰的逻辑流）。它充当了高级人类意图和低级机器执行之间的关键桥梁，与原始自然语言或冗长的编程代码相比，可以实现更精确的控制和显著更高效的与LLMs的通信。这是使伪代码成为真正可操作和可执行的工作流定义语言的关键一步。

### **3.4. 伪代码驱动AI中的状态管理和控制流**

有效的工作流编排模型，无论是传统的还是AI驱动的，本质上都依赖于跟踪状态、将复杂逻辑分解为独立步骤、智能跳过已完成步骤以及自动重试失败步骤的能力 32。StateFlow框架明确将基于LLM的任务解决过程概念化为状态机。在此模型中，任务解决过程的每个步骤都可以映射到一个不同的状态。伪代码可以精确定义每个状态内的操作序列（例如，生成LLM响应、利用外部工具），并阐明控制状态转换的规则，从而确保任务的清晰跟踪和动态进展 33。

代理AI系统维护一个“记忆”组件来存储上下文、先前任务和过去操作的结果。此记忆对于指导未来决策和规划至关重要 2。伪代码可以定义此记忆如何在代理的迭代循环中被访问、更新和利用（例如，

memory.store(subtask, result)） 2。“对话例程”通过将程序逻辑直接嵌入系统提示中进一步例证了这一点。这使得LLMs能够充当动态工作流解释器，通过人类可读的指令声明性地定义控制流，从而提供比传统硬编码方法更大的灵活性 5。

伪代码能够实现“可观察和可审计的AI代理”。伪代码用于定义AI工作流中的状态转换和内存更新 2。另外，思维链（CoT）提示旨在使LLM推理透明 35。如果整个工作流，包括其内部状态和转换，都由人类可读的伪代码定义，那么AI代理的执行路径和决策逻辑就变得透明和可检查。这类似于传统上良好文档化的代码如何提供程序执行的可审计轨迹。在复杂的AI系统中，特别是自主代理系统中，LLM决策的“黑箱”性质是一个重大问题，导致“不透明性和可解释性”问题 37 以及建立“信任”的挑战 38。通过在伪代码中定义工作流和状态转换，AI操作背后的逻辑变得明确和可检查。这直接解决了这些透明度问题，使系统行为更易于理解。这种透明度对于有效的调试、确保法规遵从性以及在实际AI部署中进行战略规划至关重要。伪代码不仅仅是“启用”状态管理；它使状态管理“透明和可审计”，从而增强了对复杂AI行为的信任、控制和问责制。

**表2：代理AI的关键特征及伪代码的作用**

| 特征 | 描述 | 伪代码的作用 |  |
| :---- | :---- | :---- | :---- |
| **规划** | 将高层目标分解为可操作的子任务。 | 伪代码定义了planner.plan(goal, memory)（规划器.规划(目标, 记忆)）等操作 2，概述了将高层目标分解为可操作子任务的逻辑 39。 |  |
| **记忆** | 存储上下文和过去结果以指导未来决策。 | 伪代码包含memory.store(subtask, result)（记忆.存储(子任务, 结果)） 2，展示了执行子任务的结果如何存储，并被规划器（ | planner.plan(goal, memory)）用于后续决策。 |
| **工具使用** | 调用外部工具（API、文件系统、Python代码等）执行任务。 | 伪代码指定了executor.execute(subtask)（执行器.执行(子任务)） 2，并详细描述了工具调用、参数传递和结果处理的逻辑 25。 |  |
| **反思** | 自我评估输出，以决定重试或继续。 | 伪代码包含了feedback \= evaluator.evaluate(result)（反馈 \= 评估器.评估(结果)）和if feedback \== "retry": planner.adjust()（如果 反馈 \== "重试": 规划器.调整()） 2，说明了自我纠正循环。 |  |
| **目标驱动** | AI代理以意图行动，而非仅仅反应。 | 伪代码通过明确定义目标（goal）和规划实现这些目标的步骤来体现这一点，如while not goal\_achieved（当未达成目标时）循环 2。 |  |
| **环境感知** | 能够与外部环境（API、文件、数据库等）交互。 | 伪代码通过明确的工具调用（executor.execute(subtask)）和对外部数据的处理（如tool\_selector.select\_appropriate\_tool）来体现这一点 25。 |  |
| **迭代性** | 反思、修改并重复步骤以达成目标。 | 伪代码的核心代理循环（while not goal\_achieved）本身就是迭代过程，包含评估反馈和调整规划的步骤 2。 |  |
| **自主性** | 具备在最小人为监督下设定目标和做出决策的能力。 | 伪代码为代理提供了高层逻辑和流程，使其能够独立地分解任务、规划执行并根据反馈采取行动 2。 |  |
| **适应性** | 根据实时反馈和环境变化调整行为。 | 伪代码中的evaluator.evaluate(result)和planner.adjust()机制直接支持代理根据执行结果调整其策略，实现动态适应 2。 |  |

## **4\. 伪代码驱动AI工作流的挑战与局限性**

### **4.1. 歧义性与缺乏通用标准化**

伪代码的主要且最显著的挑战源于其固有的性质：它通常不遵循任何特定编程语言的严格语法规则，并且缺乏系统化、普遍接受的标准形式 7。这种刻意的灵活性虽然有利于人类概念化，但却导致不同作者或上下文之间风格和解释的巨大差异 7。

因此，不同个体可能会对同一段伪代码做出不同的解释，从而在尝试自动化解释时导致潜在的误解和不一致 19。伪代码中“数学符号”的变化加剧了这个问题，这些符号可能因特定的数学领域、历史背景或作者偏好而显著不同 12。此外，某些伪代码中常见的做法，例如依赖单个字母和符号作为变量名，会大大降低可读性 12。伪代码通常省略所有符号或变量的明确定义，需要外部上下文，而这些上下文可能无法被自动化系统轻易获取 12。

这引出了“灵活性-形式化悖论”。伪代码的核心优势在于其灵活性和语言独立性 7。然而，其自动化方面的主要弱点在于缺乏标准化和固有的歧义性 7。这在尝试通过LLMs自动化解释和执行伪代码时产生了根本性的张力。伪代码之所以对人类构思和高层概念化如此吸引人（其非正式性和灵活性），恰恰成为机器可靠解释和鲁棒自动化的一大障碍。为了让伪代码能够被LLMs可靠地解释或直接“执行”，它需要某种程度的形式化或一致的语法（例如，Markdown启发式元素）。然而，引入过多的形式化可能会剥夺其“伪代码”的本质，可能将其变成一种新的、尽管简化的编程语言，这将违背寻求轻量级、以人为本的复杂工作流工具替代方案的初衷。这种内在的冲突便是“灵活性-形式化悖论”。克服这一悖论需要微妙的平衡：定义足够的结构一致性（例如，通过特定的Markdown类约定或受限语法）以实现可靠的LLM处理，同时又不牺牲语言独立性和易于概念化的核心以人为本的优势。这也意味着，用于伪代码解析、验证和潜在消歧的复杂自动化工具对于实际应用至关重要。

### **4.2. 解析复杂性与错误处理**

尽管LLMs具有令人印象深刻的能力，但在鲁棒地理解高度结构化数据（如复杂图结构）或精确解释细致、非正式的伪代码方面仍存在局限性，因为它们主要设计用于处理非结构化文本 3。它们对概率自回归解码的依赖意味着它们可能优先考虑看似合理的预测而非精确的计算，即使在看似简单的任务中也可能导致预测错误 4。

由于缺乏严格、普遍定义的语法规则 7，鲁棒地解析非正式伪代码以实现自动化执行本身就具有挑战性。这种缺乏严谨性可能导致“细节缺失和结果不正确”，如果伪代码被松散地改写成自然语言，或者关键的核心思想在转换中丢失 3。

有效的错误处理是成熟软件开发的基石 41。虽然传统的错误处理机制（例如，

try-except块、日志记录、输入验证、重试机制）在传统代码中已得到充分建立 41，但将其无缝且有效地应用于伪代码定义的工作流则引入了新的复杂性。LLM如何“调试”其在伪代码驱动工作流中的解释或执行错误？PIE框架通过结合小规模单元测试和试错技术提供了一个实用的解决方案，向LLM提供错误消息以进行迭代修正 3。

这反映了人类意图与LLM解释之间的“语义鸿沟”。伪代码是为人类阅读而设计的 7。LLMs，尽管功能强大，但在精确计算和高度结构化数据方面仍有困难 4。可靠地解析非正式伪代码是困难的 7。这表明人类直观地编写和解释伪代码的方式与LLMs处理伪代码以执行的方式之间存在根本性的不匹配。这种不匹配不仅仅是语法解析的问题；它是一个更深层次的语义理解问题。人类在伪代码中隐含地推断上下文、填补缺失的细节并解决歧义 12。LLMs，尽管具有先进的推理能力，可能并不总是做出相同的推断，或者它们可能会“幻觉”出偏离原始人类意图的细节 3。这在高级人类设计和LLM的具体解释之间造成了“语义鸿沟”。“未经测试的代码通常是不正确的” 7 这一说法在这种情况下变得尤为关键，因为LLM的“代码”（其解释和生成的动作）在语义上可能与人类的伪代码存在缺陷。PIE框架采用的迭代试错机制 3 直接承认了这种语义鸿沟，因为它试图通过持续的改进和明确的错误反馈来弥合它，有效地教会LLM将其解释与预期结果对齐。为了确保伪代码驱动的AI工作流的可靠性和正确性，复杂的验证和反馈循环是不可或缺的。这可能涉及人工干预的关键审查机制、伪代码逻辑的形式验证步骤，或AI代理内部的先进自我纠正能力，所有这些都旨在确保LLM的解释始终与原始人类设计意图保持一致。

### **4.3. 安全与可扩展性问题**

**安全性：** 如果伪代码用于定义工具调用和外部交互，则系统将固有地继承与通用LLM部署相关的安全风险。这些普遍存在的风险包括提示注入（恶意输入操纵模型行为）、敏感信息泄露（无意中泄露私人数据）、供应链漏洞（底层组件受损）、数据和模型中毒（训练数据中的恶意内容）、不当输出处理（不安全或有害的输出）、过度代理（赋予模型过多自主权）以及系统提示泄露（泄露内部配置） 11。如果伪代码赋予LLMs广泛且不受约束的权限，则“过度代理”的风险尤其相关，可能导致意外操作或未经授权的系统访问 11。

**可扩展性：** 设计可扩展的AI代理和工作流带来了重大挑战。这包括高效处理日益增长的大数据集、管理大量计算资源、确保与各种现有系统的无缝集成，以及维护大规模持续学习的机制 22。虽然伪代码本身可以很简洁 17，但底层的LLM调用和工具执行仍然消耗大量资源。LLMs本质上是资源密集型的，其性能会随着代码长度或任务复杂性的增加而急剧下降，使其不适用于低延迟、高可扩展性的应用 4。

这揭示了伪代码驱动代理中的“控制与自主性”困境。伪代码能够实现AI代理行为 2 和广泛的工具使用 25。然而，“过度代理”被明确列为关键安全风险 11。此外，可扩展性需要仔细管理计算资源 44。通过伪代码赋予AI代理更大的自主权直接引入了更高的安全和效率风险。伪代码指令越抽象和高层，LLM解释、规划和执行所需工作流所需的“代理”就越多。虽然这种增加的代理能力对于自动化复杂任务非常强大，但它直接与潜在的安全漏洞（例如，由于误解或恶意提示导致的意外操作、未经授权的访问）相关联，并且如果LLM的内部“推理”或资源分配不优化，可能会导致效率低下。核心挑战在于定义伪代码，使其既能满足人类设计的抽象性，又能同时足够受限和精确，以确保AI执行的可靠性、安全性和可扩展性。这就是“控制与自主性”困境。未来的解决方案必须侧重于为AI代理实施强大的验证、沙盒和细粒度权限机制。这可能涉及将与安全策略和资源约束相关的特定伪代码元素形式化，允许人类设计者明确定义AI代理可以操作的边界，从而减轻与增加自主性相关的风险。

**表3：伪代码在AI工作流中的优缺点**

| 类别 | 优点 | 缺点 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **优点** | **清晰度：** 比自然语言更少歧义 13。 |  简洁性： Token高效 3。 |  语言独立性： 灵活适用于各种目标语言 19。 |  LLM性能提升： 更高准确性，更好推理 13。 |  促进协作： 人类与AI之间共享理解 8。 |  易于迭代/修改： 变更的蓝图 8。 |  更好问题理解： 专注于逻辑 8。 |  减少错误： 预编码识别逻辑错误 8。 | **缺乏通用标准：** 解释多样 7。 |  解释歧义： 人类与LLM理解差异 19。 |  不可直接执行： 需要LLM/解释器 19。 |  解析复杂性： 鲁棒自动化面临挑战 7。 |  错误处理挑战： 调试LLM解释困难 3。 |  安全风险： 提示注入、过度代理、数据泄露 11。 |  可扩展性挑战： 极端复杂或大规模任务 4。 |  过度简化潜力： 可能遗漏关键细节 3。 |

## **5\. 机遇与未来方向**

### **5.1. 自动化伪代码生成与优化**

大型语言模型正日益展现出自动生成和优化提示（包括复杂伪代码结构）的能力 21。像“自动提示工程师”（APE）这样的框架专门自动化了提示生成和选择的过程，这可以应用于伪代码 47。Code2Pseudo等应用通过利用经过精确系统提示微调的LLMs，实现了实际编程代码与伪代码之间的双向转换，从而例证了这一点 50。类似地，InstructPipe利用LLMs生成AI管道的伪代码，然后将其编译执行 31。

研究表明，使用包含伪代码的指令微调数据来微调LLMs，可以显著提高其指令遵循能力和整体任务性能 21。这种方法在概念上类似于训练模型生成隐藏的思维链步骤，其中伪代码充当明确的中间推理步骤 21。

这标志着伪代码“元提示”的出现。LLMs能够生成伪代码 31 并优化提示 47。此外，用伪代码微调LLMs可以提高其性能 21。这表明LLMs可以积极协助伪代码提示的创建和改进。这种理解超越了LLMs仅仅将伪代码作为输入；它标志着一种元级别的交互，其中LLMs不仅是工作流语言的解释器，也是其设计者和优化器。APE和OPRO等框架 47 是这种提示策略自动化优化的主要例子，可以直接应用于伪代码。这种“元提示”能力有望大幅减少提示工程和工作流设计所需的人工工作量，使伪代码驱动的工作流在开发和维护方面更具可扩展性和效率。它还预示着未来AI系统能够根据实时性能反馈和不断变化的需求，动态地适应和演进其自身的内部“逻辑”（以伪代码表示）。

### **5.2. 通过伪代码实现自适应和自优化AI系统**

自优化AI系统代表了一种根本性的转变，使AI能够通过持续学习和适应，在没有直接人工干预的情况下自主地改进自身性能 37。这一过程涉及持续的反馈循环、在线和终身学习、元学习（“学习如何学习”）以及通过自我博弈进行的强化学习 37。

伪代码可以作为定义这些自适应行为逻辑的基础语言。例如，它可以描述“反思模式” 39，其中AI代理被编程为自我批评其输出、检测错误并迭代优化其性能。代理循环的核心伪代码（例如，

while not goal\_achieved: subtask \= planner.plan(goal, memory); result \= executor.execute(subtask); feedback \= evaluator.evaluate(result); if feedback \== "retry": planner.adjust()）直接说明了如何在AI系统内定义和执行迭代改进和自我纠正 2。这个循环使AI能够从其行动中学习并动态调整其策略。

伪代码可以作为AI演进的“可执行蓝图”。自优化AI系统旨在持续改进其性能 37。伪代码定义了包含反馈和调整机制的迭代代理循环 2。伪代码可以描述自优化和自适应的机制。如果伪代码定义了AI系统如何评估其性能、识别错误以及调整其内部参数或策略的逻辑，并且LLMs能够解释并根据这些伪代码采取行动，那么伪代码就成为AI自身演进过程的“可执行蓝图”。这超越了静态提示，实现了动态的、可能自我修改的AI行为 54。伪代码将代表高层级的“基因代码”或“学习规则”，AI本身可以解释，在高级场景中甚至可以修改这些规则。这预示着从纯粹的人工编程智能向AI驱动的自我改进的深刻转变。在这种背景下，伪代码是定义和理解这些复杂自适应机制的关键接口，从而开启了一个AI系统能够以最少人工干预进行学习和演进的新时代。

### **5.3. 人机协作的作用**

尽管AI取得了显著进展，但人类的洞察力对于定义正确的问题、设定有意义的目标以及引导AI产生真正有价值的结果仍然至关重要 46。伪代码凭借其人类可读和语言无关的特性，可以作为人类设计者与AI代理之间沟通和协作的有效通用语言 8。

这种方法实现了明确的职责分工：领域专家可以使用自然语言或伪代码设计和阐明复杂的对话工作流，而软件工程师则可以专注于开发和实现核心API功能和底层工具 28。伪代码大纲可以显著帮助AI编码助手生成更准确和上下文相关的代码，同时促进人类开发团队内部更好的协作和理解 46。编写高层伪代码、对其进行精炼，然后将其转换为实际代码（或用作AI生成代码的注释）的迭代过程突出了这种共生协作循环 55。

未来AI软件工程可能涉及协调“感觉式编码”（vibe coding，强调直观的、人机交互的、用于创意构思和快速原型开发的方法）和“代理式编码”（agentic coding，通过目标驱动的代理实现自主软件开发）的优势。伪代码有望成为连接这两种范式的关键桥梁，促进统一的开发生命周期 56。

伪代码可以作为人机团队的“共享心智模型”。伪代码能够有效促进人类协作 8，也能提高LLM的代码生成和理解能力 20。伪代码是人类和AI协作者之间有效的沟通工具。伪代码之所以能作为同时适用于人类和AI的独特沟通工具，是因为它为人类抽象了特定语言语法的认知负担，同时保留了LLMs经过预训练能够解释的基本逻辑结构。这使得人类和AI能够在一个关于问题解决方案及其高层执行流程的“共享心智模型”上进行操作，显著减少了误解，并确保了意图的一致性。这使得伪代码不仅是一种提示输入，更是一种协作产物，促进了更共生的关系。它成为人类表达高层设计和战略意图的主要媒介，而AI则提供结构化、高效的执行和详细的实现。这种协作框架对于将人类创造力和问题解决能力与AI强大的处理和代码生成能力相结合至关重要。

## **6\. 结论与建议**

### **伪代码潜力的总结与当前局限性**

伪代码为实现更直观、高效和灵活的AI工作流编排提供了一条引人注目且可能具有变革性的路径。它利用其固有的清晰度、简洁性和语言独立性，显著增强了LLM性能，减少了指令中的歧义，并降低了计算开销。其在定义多步骤过程和编排复杂工具调用方面的已验证能力，特别是在通过结构化语法（例如，Markdown启发式元素）增强时，使其成为更复杂和僵化的传统外部工作流工具的强大而轻量级的替代方案。

然而，将伪代码作为主要工作流定义语言并非没有挑战。缺乏通用标准及其在解释中固有的歧义性仍然是重大障碍。对非正式伪代码进行鲁棒解析和有效错误处理以实现自动化执行是复杂的技术问题。此外，关键的安全问题，特别是与赋予AI代理广泛权限时“过度代理”风险相关的安全问题，需要仔细考虑和强大的缓解策略。

### **未来研究与开发以有效利用伪代码在AI工作流编排中的建议**

为了充分发挥伪代码在AI工作流编排中的潜力，以下是未来研究和开发的关键建议：

* **开发标准化、Markdown启发的伪代码方言：** 未来的努力应侧重于协作开发和广泛采用半形式化的伪代码语法。这些方言应在人类可读性和概念易用性与可靠机器可解释性所需的精确性之间取得精妙平衡，并可利用已建立的Markdown扩展、类似YAML的结构或其他轻量级标记语言。这种标准化将直接解决当前歧义和解析复杂性的挑战。  
* **推进伪代码的自动化生成和优化：** 大力投入研究和开发复杂的LLM驱动工具，使其能够从高层自然语言需求中自动生成高质量的伪代码。这些工具还应能够根据实时执行反馈、性能指标和对指定约束的遵守情况，迭代地优化生成的伪代码。这将显著加速工作流设计和提示工程过程，减少人工工作量。  
* **集成鲁棒的验证和调试框架：** 开发先进的工具和方法，用于验证伪代码定义工作流的逻辑一致性和正确性。这包括创建清晰、可操作的调试反馈机制，能够在AI代理在执行过程中遇到问题时精确定位错误，可能通过将执行映射回伪代码的可视化调试界面实现。  
* **为伪代码驱动的代理实施细粒度安全控制：** 设计并集成允许直接在伪代码中定义和强制执行细粒度权限、访问控制和操作约束的机制。这对于将代理自主权限制在特定、授权的操作范围内，并防止生产环境中与“过度代理”或意外行为相关的风险至关重要。  
* **探索混合人机设计范式：** 促进跨学科研究，探索新颖的协作环境，其中人类设计者和AI代理共同创建、完善和优化伪代码工作流。这种方法将利用人类的创造力和领域专业知识进行高层设计和战略决策，同时利用AI的能力进行详细实现、优化和迭代完善，从而巩固伪代码作为人机团队的共享“语言”。  
* **建立伪代码驱动工作流的综合基准：** 开发新的、严格的基准，专门用于评估伪代码编排的AI系统的准确性、效率、鲁棒性和安全性。这些基准应涵盖复杂、多轮任务、复杂的推理挑战和现实世界的应用场景，以清晰衡量进展并识别现有差距。

#### **引用的著作**

1. Auto-Differentiating Any LLM Workflow: A Farewell to Manual Prompting \- arXiv, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2501.16673v1](https://arxiv.org/html/2501.16673v1)  
2. Agentic AI: A Complete Guide to Autonomous AI Agents \- VideoSDK, 访问时间为 六月 17, 2025， [https://www.videosdk.live/developer-hub/ai\_agent/agentic-ai](https://www.videosdk.live/developer-hub/ai_agent/agentic-ai)  
3. Pseudocode-Injection Magic: Enabling LLMs to Tackle Graph ..., 访问时间为 六月 17, 2025， [https://arxiv.org/abs/2501.13731](https://arxiv.org/abs/2501.13731)  
4. Pseudocode-Injection Magic: Enabling LLMs to Tackle Graph Computational Tasks \- arXiv, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2501.13731v1](https://arxiv.org/html/2501.13731v1)  
5. Conversation Routines: A Prompt Engineering Framework for Task-Oriented Dialog Systems, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2501.11613v1](https://arxiv.org/html/2501.11613v1)  
6. Pseudocode: What It Is and How to Write It | Built In, 访问时间为 六月 17, 2025， [https://builtin.com/data-science/pseudocode](https://builtin.com/data-science/pseudocode)  
7. Pseudocode \- Wikipedia, 访问时间为 六月 17, 2025， [https://en.wikipedia.org/wiki/Pseudocode](https://en.wikipedia.org/wiki/Pseudocode)  
8. What is pseudocode, and how do you use it? \- SoftTeco, 访问时间为 六月 17, 2025， [https://softteco.com/blog/what-is-pseudocode](https://softteco.com/blog/what-is-pseudocode)  
9. Mastering Pseudocode: Algorithm Writing Tips, Examples, and Benefits \- Toolify.ai, 访问时间为 六月 17, 2025， [https://www.toolify.ai/ai-news/mastering-pseudocode-algorithm-writing-tips-examples-and-benefits-1328440](https://www.toolify.ai/ai-news/mastering-pseudocode-algorithm-writing-tips-examples-and-benefits-1328440)  
10. Pseudocode Flowchart Guide: How Does It Enhance Your Coding \- Boardmix, 访问时间为 六月 17, 2025， [https://boardmix.com/knowledge/pseudocode-flowchart/](https://boardmix.com/knowledge/pseudocode-flowchart/)  
11. Large Language Model (LLM) Security Risks and Best Practices, 访问时间为 六月 17, 2025， [https://www.legitsecurity.com/aspm-knowledge-base/llm-security-risks](https://www.legitsecurity.com/aspm-knowledge-base/llm-security-risks)  
12. Pseudo-code is harder then actual code : r/learnprogramming \- Reddit, 访问时间为 六月 17, 2025， [https://www.reddit.com/r/learnprogramming/comments/1f5pn6q/pseudocode\_is\_harder\_then\_actual\_code/](https://www.reddit.com/r/learnprogramming/comments/1f5pn6q/pseudocode_is_harder_then_actual_code/)  
13. Prompting with Pseudo-Code Instructions \- OpenReview, 访问时间为 六月 17, 2025， [https://openreview.net/forum?id=2prcotJejU](https://openreview.net/forum?id=2prcotJejU)  
14. (PDF) Prompting with Pseudo-Code Instructions \- ResearchGate, 访问时间为 六月 17, 2025， [https://www.researchgate.net/publication/370938067\_Prompting\_with\_Pseudo-Code\_Instructions](https://www.researchgate.net/publication/370938067_Prompting_with_Pseudo-Code_Instructions)  
15. Prompting with Pseudo-Code Instructions \- ACL Anthology, 访问时间为 六月 17, 2025， [https://aclanthology.org/2023.emnlp-main.939/](https://aclanthology.org/2023.emnlp-main.939/)  
16. (PDF) Training with Pseudo-Code for Instruction Following \- ResearchGate, 访问时间为 六月 17, 2025， [https://www.researchgate.net/publication/392085257\_Training\_with\_Pseudo-Code\_for\_Instruction\_Following](https://www.researchgate.net/publication/392085257_Training_with_Pseudo-Code_for_Instruction_Following)  
17. Prompt engineering: PSEUDOCODE in prompt : r/ChatGPTPro \- Reddit, 访问时间为 六月 17, 2025， [https://www.reddit.com/r/ChatGPTPro/comments/1ip79qu/prompt\_engineering\_pseudocode\_in\_prompt/](https://www.reddit.com/r/ChatGPTPro/comments/1ip79qu/prompt_engineering_pseudocode_in_prompt/)  
18. Chain of Grounded Objectives: Concise Goal-oriented Prompting for Code Generation \- arXiv, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2501.13978v2](https://arxiv.org/html/2501.13978v2)  
19. How to Write Pseudo Code? \- Scaler Topics, 访问时间为 六月 17, 2025， [https://www.scaler.com/topics/how-to-write-pseudo-code/](https://www.scaler.com/topics/how-to-write-pseudo-code/)  
20. Few-Shot Prompting: Techniques, Examples, and Best Practices \- DigitalOcean, 访问时间为 六月 17, 2025， [https://www.digitalocean.com/community/tutorials/\_few-shot-prompting-techniques-examples-best-practices](https://www.digitalocean.com/community/tutorials/_few-shot-prompting-techniques-examples-best-practices)  
21. Training with Pseudo-Code for Instruction Following \- arXiv, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2505.18011v1](https://arxiv.org/html/2505.18011v1)  
22. Agent Architectures and Scalability: Building Robust AI Systems \- SmythOS, 访问时间为 六月 17, 2025， [https://smythos.com/developers/tool-usage/agent-architectures-and-scalability/](https://smythos.com/developers/tool-usage/agent-architectures-and-scalability/)  
23. The Role of Pseudocode in Problem Solving: A Comprehensive ..., 访问时间为 六月 17, 2025， [https://algocademy.com/blog/the-role-of-pseudocode-in-problem-solving-a-comprehensive-guide/](https://algocademy.com/blog/the-role-of-pseudocode-in-problem-solving-a-comprehensive-guide/)  
24. How AI in Software Development is Changing Workflows \- Solvo, 访问时间为 六月 17, 2025， [https://solvoglobal.com/blog/ai-in-software-development/](https://solvoglobal.com/blog/ai-in-software-development/)  
25. Write AI agent from scratch without LangChain and CrewAI \- DEV ..., 访问时间为 六月 17, 2025， [https://dev.to/franzwong/write-ai-agent-from-scratch-without-langchain-and-crewai-2bop](https://dev.to/franzwong/write-ai-agent-from-scratch-without-langchain-and-crewai-2bop)  
26. Vibe Coding vs. Agentic Coding: Fundamentals and Practical Implications of Agentic AI, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2505.19443v1](https://arxiv.org/html/2505.19443v1)  
27. Best Flowise AI Alternatives for Workflows and Orchestration \- Eden AI, 访问时间为 六月 17, 2025， [https://www.edenai.co/post/best-flowise-ai-alternatives-for-workflows-and-orchestration](https://www.edenai.co/post/best-flowise-ai-alternatives-for-workflows-and-orchestration)  
28. Conversation Routines: A Prompt Engineering Framework for Task-Oriented Dialog Systems, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2501.11613v3](https://arxiv.org/html/2501.11613v3)  
29. Pseudocode \- An obsidian plugin that helps to render a LaTeX-style pseudocode inside a code block. \- Obsidian Stats, 访问时间为 六月 17, 2025， [https://www.obsidianstats.com/plugins/pseudocode-in-obs](https://www.obsidianstats.com/plugins/pseudocode-in-obs)  
30. Show HN: Transform your codebase into a single Markdown doc for feeding into AI | Hacker News, 访问时间为 六月 17, 2025， [https://news.ycombinator.com/item?id=43048027](https://news.ycombinator.com/item?id=43048027)  
31. InstructPipe: Generating Visual Blocks pipelines with human instructions and LLMs, 访问时间为 六月 17, 2025， [https://research.google/blog/instructpipe-generating-visual-blocks-pipelines-with-human-instructions-and-llms/](https://research.google/blog/instructpipe-generating-visual-blocks-pipelines-with-human-instructions-and-llms/)  
32. How Serverless Workflows Actually Work? | Upstash Blog, 访问时间为 六月 17, 2025， [https://upstash.com/blog/workflow-orchestration](https://upstash.com/blog/workflow-orchestration)  
33. StateFlow: Enhancing LLM Task-Solving through State-Driven Workflows \- arXiv, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2403.11322v1](https://arxiv.org/html/2403.11322v1)  
34. \[2501.11613\] Conversation Routines: A Prompt Engineering Framework for Task-Oriented Dialog Systems \- arXiv, 访问时间为 六月 17, 2025， [https://arxiv.org/abs/2501.11613](https://arxiv.org/abs/2501.11613)  
35. What is chain of thought (CoT) prompting? \- IBM, 访问时间为 六月 17, 2025， [https://www.ibm.com/think/topics/chain-of-thoughts](https://www.ibm.com/think/topics/chain-of-thoughts)  
36. AI Prompting (2/10): Chain-of-Thought Prompting—4 Methods for Better Reasoning \- Reddit, 访问时间为 六月 17, 2025， [https://www.reddit.com/r/ChatGPTPromptGenius/comments/1if2dai/ai\_prompting\_210\_chainofthought\_prompting4/](https://www.reddit.com/r/ChatGPTPromptGenius/comments/1if2dai/ai_prompting_210_chainofthought_prompting4/)  
37. Self-Optimizing AI \- Unaligned Newsletter, 访问时间为 六月 17, 2025， [https://www.unaligned.io/p/self-optimizing-ai](https://www.unaligned.io/p/self-optimizing-ai)  
38. Pseudocode to parse the honeypot data, leveraging LLM. \- ResearchGate, 访问时间为 六月 17, 2025， [https://www.researchgate.net/figure/Pseudocode-to-parse-the-honeypot-data-leveraging-LLM\_fig5\_381683261](https://www.researchgate.net/figure/Pseudocode-to-parse-the-honeypot-data-leveraging-LLM_fig5_381683261)  
39. Agentic AI and the Next Generation of AI Assistants | Nitor Infotech, 访问时间为 六月 17, 2025， [https://www.nitorinfotech.com/blog/agentic-ai-and-the-next-generation-of-ai-assistants/](https://www.nitorinfotech.com/blog/agentic-ai-and-the-next-generation-of-ai-assistants/)  
40. I absolutely do not understand pseudo code. : r/learnprogramming \- Reddit, 访问时间为 六月 17, 2025， [https://www.reddit.com/r/learnprogramming/comments/1jtz96z/i\_absolutely\_do\_not\_understand\_pseudo\_code/](https://www.reddit.com/r/learnprogramming/comments/1jtz96z/i_absolutely_do_not_understand_pseudo_code/)  
41. Error Handling: A Guide to Preventing Unexpected Crashes \- Sonar, 访问时间为 六月 17, 2025， [https://www.sonarsource.com/learn/error-handling-guide/](https://www.sonarsource.com/learn/error-handling-guide/)  
42. Basic AI Prompts for Developers: Practical Examples for Everyday Tasks \- Portkey, 访问时间为 六月 17, 2025， [https://portkey.ai/blog/basic-ai-prompts-for-developers](https://portkey.ai/blog/basic-ai-prompts-for-developers)  
43. Analysing Safety Risks in LLMs Fine-Tuned with Pseudo-Malicious Cyber Security Data, 访问时间为 六月 17, 2025， [https://arxiv.org/html/2505.09974v1](https://arxiv.org/html/2505.09974v1)  
44. Scalable AI Agent Architecture: Benefits, Challenges, and Use Cases \- Debut Infotech, 访问时间为 六月 17, 2025， [https://www.debutinfotech.com/blog/scalable-ai-agent-architecture](https://www.debutinfotech.com/blog/scalable-ai-agent-architecture)  
45. (PDF) Enhancing LLMs in Long Code Translation through Instrumentation and Program State Alignment \- ResearchGate, 访问时间为 六月 17, 2025， [https://www.researchgate.net/publication/390468677\_Enhancing\_LLMs\_in\_Long\_Code\_Translation\_through\_Instrumentation\_and\_Program\_State\_Alignment](https://www.researchgate.net/publication/390468677_Enhancing_LLMs_in_Long_Code_Translation_through_Instrumentation_and_Program_State_Alignment)  
46. Built to Last in an AI Future \- Insights@Questrom \- Boston University, 访问时间为 六月 17, 2025， [https://insights.bu.edu/built-to-last-in-an-ai-future/](https://insights.bu.edu/built-to-last-in-an-ai-future/)  
47. Automated Prompt Engineering: How does it work? \- DataScientest, 访问时间为 六月 17, 2025， [https://datascientest.com/en/all-about-automated-prompt-engineering](https://datascientest.com/en/all-about-automated-prompt-engineering)  
48. Automatic Prompt Engineer (APE), 访问时间为 六月 17, 2025， [https://www.promptingguide.ai/techniques/ape](https://www.promptingguide.ai/techniques/ape)  
49. Automated Prompt Engineering: The Definitive Hands-On Guide | Towards Data Science, 访问时间为 六月 17, 2025， [https://towardsdatascience.com/automated-prompt-engineering-the-definitive-hands-on-guide-1476c8cd3c50/](https://towardsdatascience.com/automated-prompt-engineering-the-definitive-hands-on-guide-1476c8cd3c50/)  
50. AI app: Code2Pseudo for Trae AI IDE: Zero Limits Hackathon, 访问时间为 六月 17, 2025， [https://lablab.ai/event/code-craft-ai-x-dev-hackathon/code-catalysts/code2pseudo](https://lablab.ai/event/code-craft-ai-x-dev-hackathon/code-catalysts/code2pseudo)  
51. \[2505.18011\] Training with Pseudo-Code for Instruction Following \- arXiv, 访问时间为 六月 17, 2025， [https://arxiv.org/abs/2505.18011](https://arxiv.org/abs/2505.18011)  
52. Adaptive AI: The Key to Dynamic Decision-Making \- Binariks, 访问时间为 六月 17, 2025， [https://binariks.com/blog/adaptive-ai-guide/](https://binariks.com/blog/adaptive-ai-guide/)  
53. Mastering Adaptive AI: A Step-by-Step Implementation Guide \- Rejolut, 访问时间为 六月 17, 2025， [https://rejolut.com/blog/implement-adaptive-ai/](https://rejolut.com/blog/implement-adaptive-ai/)  
54. Self-modifying code \- Wikipedia, 访问时间为 六月 17, 2025， [https://en.wikipedia.org/wiki/Self-modifying\_code](https://en.wikipedia.org/wiki/Self-modifying_code)  
55. Hot Take: Learning Pseudocode is more important than coding in ..., 访问时间为 六月 17, 2025， [https://www.reddit.com/r/learnprogramming/comments/1iffahn/hot\_take\_learning\_pseudocode\_is\_more\_important/](https://www.reddit.com/r/learnprogramming/comments/1iffahn/hot_take_learning_pseudocode_is_more_important/)  
56. Vibe Coding vs. Agentic Coding: Fundamentals and Practical Implications of Agentic AI \- arXiv, 访问时间为 六月 17, 2025， [https://arxiv.org/pdf/2505.19443](https://arxiv.org/pdf/2505.19443)