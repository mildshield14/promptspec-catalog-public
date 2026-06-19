# PromptSpec Pattern Catalog

> **Read this if you just want the taxonomy.** This is the MD view of the catalog. The machine-readable source of truth is [`catalog/patterns.json`](catalog/patterns.json) — if the two ever disagree, the JSON wins.

The catalog contains **29 prompt-engineering patterns** across **5 categories**.

All patterns in this catalog are derived from published prompt-engineering literature. They are taxonomy entries, not empirically observed corpus findings.

Each pattern lists the **prompt component type(s)** it relates to in the PromptSpec model (`PROFILE_ROLE`, `DIRECTIVE`, `CONTEXT`, `WORKFLOW`, `EXAMPLES`, `OUTPUT_FORMAT`, `CONSTRAINTS`). The binding *semantics* (whether a pattern is primary in, modifies, or spans those components) are defined in the associated publication, not in this catalog.

## Summary

| Pattern | Category | Component(s) |
|---|---|---|
| FewShot | In-Context Learning | `EXAMPLES` |
| ZeroShot | In-Context Learning | `DIRECTIVE` |
| ChainOfThought | Reasoning | `WORKFLOW` |
| ComplexCoT | Reasoning | `WORKFLOW` |
| LeastToMost | Reasoning | `WORKFLOW` |
| PlanAndSolve | Reasoning | `WORKFLOW` |
| ReverseCoT | Reasoning | `WORKFLOW` |
| StructuredCoT | Reasoning | `WORKFLOW` |
| FactCheckList | Output Control | `CONSTRAINTS` |
| OutputAutomater | Output Control | `OUTPUT_FORMAT` |
| Persona | Output Control | `PROFILE_ROLE` |
| Recipe | Output Control | `WORKFLOW` |
| Reflection | Output Control | `WORKFLOW` |
| SchemaSpecs | Output Control | `OUTPUT_FORMAT` |
| SelfCalibration | Output Control | `CONSTRAINTS` |
| SelfVerification | Output Control | `CONSTRAINTS`, `WORKFLOW` | 
| Template | Output Control | `OUTPUT_FORMAT` |
| VisualizationGenerator | Output Control | `OUTPUT_FORMAT` |
| ContextManager | Context Control | `CONTEXT`, `DIRECTIVE`, `WORKFLOW` |
| AlternativeApproaches | Meta-Directives | `WORKFLOW` |
| CognitiveVerifier | Meta-Directives | `WORKFLOW` |
| FlippedInteraction | Meta-Directives | `DIRECTIVE`, `WORKFLOW` |
| GamePlay | Meta-Directives | `DIRECTIVE`, `CONSTRAINTS` |
| InfiniteGeneration | Meta-Directives | `DIRECTIVE`, `WORKFLOW` |
| InstructionSelection | Meta-Directives | `DIRECTIVE` |
| QuestionRefinement | Meta-Directives | `DIRECTIVE` |
| RAR | Meta-Directives | `WORKFLOW` |
| RE2 | Meta-Directives | `OUTPUT_FORMAT` |
| RefusalBreaker | Meta-Directives | `DIRECTIVE` |

## In-Context Learning

### FewShot

Provide exemplar input-output pairs to guide the model.

**Component(s):** `EXAMPLES`

*Placeholder form:*

```
Instruction: {QUESTION}
Examples:
Input: {EXAMPLE_INPUT_1}
Output: {EXAMPLE_OUTPUT_1}
Input: {EXAMPLE_INPUT_2}  Output: {EXAMPLE_OUTPUT_2}

Now apply to: {INPUT_DATA}
```

*Example:*

```
Translate English to French.

Examples:
Input: Night
Output: Nuit
Input: Morning
Output: Matin
Input: Fall
Output: Automne

Now apply to:
Winter
```

> Mutually exclusive with ZeroShot.

### ZeroShot

Provide no examples to guide the task; rely on direct instructions plus input data.

**Component(s):** `DIRECTIVE`  

*Placeholder form:*

```
Instruction: {QUESTION}
Input data: {INPUT_DATA}
```

*Example:*

```
Translate the following English word to French.

Input: Morning
```

> Represents the default prompting strategy when no demonstrations are provided.


## Reasoning

### ChainOfThought

Encourage generic step-by-step reasoning before the final answer.

**Component(s):** `WORKFLOW` 

*Placeholder form:*

```
Let’s think step by step.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Let’s think step by step.

Solve the following math problem:

Roger has 5 apples and gives 2 to Josh and 1 to Jane. How much is left?
```

### ComplexCoT

During decoding, selects answers from the most complex reasoning chains.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
Generate multiple reasoning paths: {PATH_1}, {PATH_2}, …

Compare results across paths.

Select the most consistent final answer.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Solve the following problem step by step. Generate multiple possible reasoning paths.
Compare the answers and select the most consistent final answer.

Solve the following math problem:
A shop had 50 pens. They sold 18 on Monday and 12 on Tuesday. How many pens remain?
```

### LeastToMost

Decompose into easiest sub-problems first, then harder ones.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
{QUESTION}
{INPUT_DATA}

Decompose problem into simpler subproblems: {SUBPROBLEM_1}, {SUBPROBLEM_2}, …

Solve each subproblem in sequence.

Combine subproblem solutions into final answer.
```

*Example:*

```
Solve the following problem step by step. First, decompose the problem into smaller subproblems.
Then, solve each subproblem in sequence.
Finally, combine the solutions to produce the final answer.

Question:
A school cafeteria has 312 apples. They want to distribute them equally to 24 students. Each student eats 2 apples, and the rest are saved. How many apples are saved?
```

### PlanAndSolve

First plan sub-problems, then solve them step by step.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
Step 1: Generate a high-level plan of solution steps: {PLAN}
Step 2: Execute each step in order.
Step 3: Produce final answer.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
First, generate a clear plan outlining the steps needed to solve the problem.
Then, follow the plan step by step to produce the final answer.

Question:
If a train travels 120 km in 2 hours, and then 180 km in 3 hours, what is its average speed across the whole trip?
```

### ReverseCoT

Generate reasoning steps after giving the answer, to simulate justification.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
{QUESTION}
{INPUT_DATA}

First, output the final answer only.
Then, generate the reasoning steps that justify the answer.
```

*Example:*

```
Please answer the question.
First, state the final answer directly.
Then, explain the reasoning that justifies your answer.
 “The answer is 57. Reasoning: Because 23+47…”
```

### StructuredCoT

Structure reasoning with program-like constructs such as sequencing, branching, and looping.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
Use structured reasoning constructs:
- Sequencing: {STEP_1}, {STEP_2}, …
- Branching: IF {CONDITION} THEN {ACTION}
- Looping: FOR {ITEM} IN {SET} DO {ACTION}
End with final answer.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Sequencing: Initialize sum = 0
Looping: FOR i=1..10 IF i is even THEN sum += i
End with final answer.
```


## Output Control

### FactCheckList

Use a checklist to confirm factual accuracy of the output.

**Component(s):** `CONSTRAINTS`  

*Placeholder form:*

```
Extract facts from output: {FACT_1}, {FACT_2}, …

Insert fact list at {OUTPUT_LOCATION}

Ensure facts are fundamental to correctness.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Extract facts from output: {Capital of Australia = Canberra}

Insert fact list at end of answer

Ensure facts are fundamental to correctness.
```

### OutputAutomater

Captures instructions that constrain the LLM response into a machine-readable, directly reusable, or output-only format, such as JSON, tables, lists, or explicitly formatted sections.

**Component(s):** `OUTPUT_FORMAT`  

*Placeholder form:*

```
Return only {OUTPUT_FORMAT}.
Include these fields or columns: {FIELD_1}, {FIELD_2}, {FIELD_3}.
Do not include explanatory prose outside the formatted output.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Return only JSON with the keys "task", "priority", and "owner".
Do not include markdown fences or explanatory prose.

Summarize this request as a task record:
Please have Maya review the launch checklist by Friday. It is high priority.
```

### Persona

Adopt a role/persona to shape style and voice.

**Component(s):** `PROFILE_ROLE`  

*Placeholder form:*

```
Act as {PERSONA}
Provide outputs that {PERSONA} would create

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Act as a helpful math tutor.
Provide outputs that a helpful math tutor would create

Explain how to solve the following equation step by step:
2x + 5 = 15
```

### Recipe

Provide a repeatable recipe-style sequence for solving tasks.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
I would like to achieve {INPUT_DATA}.
Provide a complete sequence of steps for me.
Fill in any missing steps.
Identify any unnecessary steps.
```

*Example:*

```
List ordered steps: STEP_1 = Preheat oven, STEP_2 = Mix flour and sugar, STEP_3 = Bake for 30 minutes
Fill in missing steps if necessary.
Identify unnecessary steps if present.
```

### Reflection

Model reflects on its first output, critiques it, and produces a revised answer.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
Step 1: Generate initial answer: {ANSWER_1}
Step 2: Critique reasoning and assumptions in {ANSWER_1}
Step 3: Revise output based on critique.
Final Answer = {ANSWER_REVISED}


{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Whenever you generate an answer
Explain the reasoning and assumptions behind your
answer
(Optional) ...so that I can improve my question
```

### SchemaSpecs

Define an explicit schema or required fields that the model output must follow.

**Component(s):** `OUTPUT_FORMAT`  

*Placeholder form:*

```
Force output into schema: {SCHEMA}

Populate schema fields: {FIELD_1}, {FIELD_2}, …

{QUESTION}
```

*Example:*

```
Output must follow schema: {Title:…, Author:…, Year:…}”
```

### SelfCalibration

Model adjusts confidence in its answer or re-calibrates if uncertain.

**Component(s):** `CONSTRAINTS`  

*Placeholder form:*

```
Generate multiple reasoning paths: {PATH_1}, {PATH_2}, …

Evaluate confidence of each path: {CONFIDENCE_1}, {CONFIDENCE_2}, …

Adjust or recalibrate answer based on confidence distribution.

Final Answer = {CALIBRATED_ANSWER}

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Generate multiple independent reasoning paths.
Compare the results and select the most consistent final answer.

Question:
What is 27 + 36?
```

### SelfVerification

Ask the model to verify its own answer against explicit constraints before finalizing.

**Component(s):** `CONSTRAINTS`, `WORKFLOW`  

*Placeholder form:*

```
Step 1: Generate an initial answer: {ANSWER_1}

Step 2: Verify whether {ANSWER_1} satisfies constraints: {CONSTRAINTS}

Step 3: If verification fails, explain issue and correct.

Final Answer = {VERIFIED_ANSWER}

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Step 1: Generate an initial answer.
Step 2: Verify whether the answer satisfies the requirements.
Step 3: If verification fails, explain the issues.
Final Answer: {final answer}

Question:
What is the capital of Australia?
Final Answer: Canberra
```

### Template

Preserve a provided human-readable prose template or textual layout.

**Component(s):** `OUTPUT_FORMAT`  

*Placeholder form:*

```
Use template: {TEMPLATE}

Insert content into placeholders: {PLACEHOLDER_1}, {PLACEHOLDER_2}, …

Preserve formatting of template.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Use this template for every response:

Title: {TITLE}
Summary: {SUMMARY}
Next Steps:
1. {STEP_ONE}
2. {STEP_TWO}

Fill the placeholders for a project status update about migrating a documentation site. Preserve the labels, numbering, and line breaks.
```

### VisualizationGenerator

Generate visual or tabular representations for tools such as charting libraries.

**Component(s):** `OUTPUT_FORMAT` 

*Placeholder form:*

```
Generate visualization: {VISUALIZATION_TYPE}

Structure data for tool: {TOOL}

Output must be formatted for visualization.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Generate visualization: bar chart
Structure data for tool: matplotlib
Output must be formatted for visualization.
```


## Context Control

### ContextManager

Explicitly control what context the model uses to avoid drift.

**Component(s):** `CONTEXT`, `DIRECTIVE`, `WORKFLOW`  

*Placeholder form:*

```
Set scope: {SCOPE}
Include only: {INCLUDE_ITEMS}
Exclude always: {EXCLUDE_ITEMS}
If signal = "reset", discard accumulated context and restart within {SCOPE}.

{QUESTION}
{INPUT_DATA}
```

*Example:*

```
Within scope X
Please consider Y
Please ignore Z
(Optional) start over
```


## Meta-Directives

### AlternativeApproaches

Suggest multiple different ways to solve the same problem.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
Given input task: {TASK}

List alternative approaches: {APPROACH_1}, {APPROACH_2}, …

(Optional) Compare pros/cons of each.

{QUESTION}
```

*Example:*

```
Within scope X, if there are alternative ways to accom-
plish the same thing, list the best alternate approaches
(Optional) compare/contrast the pros and cons of each
approach
(Optional) include the original way that I asked
(Optional) prompt me for which approach I would like
to use
```

### CognitiveVerifier

Add explicit verification of reasoning correctness via sub-questions.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
Given input question: {QUESTION}

Generate subquestions: {Q1}, {Q2}, …

Answer each subquestion.
Combine subanswers into final answer.
```

*Example:*

```
When you are asked a question, follow these rules
Generate a number of additional questions that would
help more accurately answer the question
Combine the answers to the individual questions to
produce the final answer to the overall question
```

### FlippedInteraction

Model asks the user questions instead of directly answering.

**Component(s):** `DIRECTIVE`, `WORKFLOW`  

*Placeholder form:*

```
Instead of answering directly:
Generate subquestions to ask user: {Q1}, {Q2}, …

Stop when {GOAL_CONDITION} is satisfied.

{QUESTION}
```

*Example:*

```
I would like you to ask me questions to achieve X
You should ask questions until this condition is met or
to achieve this goal (alternatively, forever)
(Optional) ask me the questions one at a time, two at
a time, etc.
```

### GamePlay

Frame the task as a game to increase engagement.

**Component(s):** `DIRECTIVE`, `CONSTRAINTS`  

*Placeholder form:*

```
Frame task as a game: {GAME_NAME}

Define rules: {RULE_1}, {RULE_2}, …

Interaction must proceed according to rules.

{QUESTION}
```

*Example:*

```
Create a game around practicing French vocabulary.
The game must define one or more fundamental rules.
The rules should constrain how the user can respond.
The interaction must proceed according to the defined rules.
```

### InfiniteGeneration

Model generates continuously, with prompts to keep going.

**Component(s):** `DIRECTIVE`, `WORKFLOW`  

*Placeholder form:*

```
Continuously generate {OUTPUT_TYPE}

Batch size = {N} outputs per turn

Stop when {STOP_CONDITION}

{QUESTION}
```

*Example:*

```
I would like you to generate a name
and job forever. I am going to provide a
template for your output. Everything in all caps is a
placeholder. Any time that you generate text, try to
fit it into one of the placeholders that I list. Please
preserve the formatting and overall template that I
provide: https://myapi.com/NAME/profile/JOB
```

### InstructionSelection

Choose the best instruction from a set of candidates.

**Component(s):** `DIRECTIVE`  

*Placeholder form:*

```
Given candidate instructions: {INST_1}, {INST_2}, … {INST_N}
Select best instruction for task: {BEST_INST}

{QUESTION}
```

*Example:*

```
Candidate prompts: A, B, C → Pick best for task.
```

### QuestionRefinement

Improve or reformulate the user's query for clarity.

**Component(s):** `DIRECTIVE`  

*Placeholder form:*

```
Take input query: {RAW_QUESTION}

Suggest a refined version: {REFINED_QUESTION}

(Optional) Ask user to confirm refinement.

{QUESTION}
```

*Example:*

```
Within scope of cybersecurity and security risks, suggest a better version of the question
to use instead
(Optional) prompt me if I would like to use the better
version instead

How to use Windows?
```

### RAR

Retrieve info, answer, then refine with self-edit.

**Component(s):** `WORKFLOW`  

*Placeholder form:*

```
Step 1: Retrieve relevant context: {CONTEXT}
Step 2: Generate answer from {CONTEXT}
Step 3: Refine answer for clarity/completeness

{QUESTION}
```

*Example:*

```
“Step 1: Retrieve passage. Step 2: Answer. Step 3: Refine answer.”
```

### RE2

Force output into reasoning, evidence, explanation structure.

**Component(s):** `OUTPUT_FORMAT`  

*Placeholder form:*

```
Format output with sections:
Reason: {REASON}
Evidence: {EVIDENCE}
Explanation: {EXPLANATION}

{QUESTION}
```

*Example:*

```
“Reason: … Evidence: … Explanation: …”
```

### RefusalBreaker

Reframe a request when the model refuses; mainly an on-refusal fallback pattern.

**Component(s):** `DIRECTIVE`  

*Placeholder form:*

```
If refusal occurs:
Step 1: State refusal reason.
Step 2: Reframe request into 
alternative query: {ALT_QUERY}

{QUESTION}
```

*Example:*

```
Whenever you can’t answer a question
Explain why you can’t answer the question
Provide one or more alternative wordings of the ques-
tion that you could answer
```


---

*Generated from `catalog/patterns.json`. Regenerate after editing the JSON so the two stay in sync.*
