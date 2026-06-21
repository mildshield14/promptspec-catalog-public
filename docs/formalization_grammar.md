# PromptSpec Formalization Grammar

Each pattern formalization lives in `method/formalizations/<pattern_id>.promptspec`.
`catalog/patterns.json` is generated; its `formalization` fields are populated from
those files by `scripts/build_catalog.py`. 

The validators check syntax and top-level shape only. They do not certify that a
formalization is semantically correct for the research taxonomy.

```text
PatternSpec   ::= 'pattern' NAME 'category' CATEGORY 'variables' VariableBlock 'template' TemplateBlock
                  ('trigger' TriggerType)? ('compatible' '[' NAME (',' NAME)* ']')?
VariableBlock ::= '{' VariableDef* '}'
VariableDef   ::= NAME Cardinality ':' VarType ('=' DefaultValue)? ('|' AllowedValues)? (STRING)?
Cardinality   ::= '*'(required) | '?'(optional) | '+'(one-or-more) | '...'(zero-or-more)
VarType       ::= 'string' | 'int' | 'bool' | 'list' | 'enum'
TemplateBlock ::= '```' TemplateContent '```'
Segment       ::= FixedText | Variable | Conditional | Loop
Variable      ::= '{{' NAME '}}'
Conditional   ::= '{{#' NAME '}}' TemplateContent '{{/' NAME '}}'
Loop          ::= '{{^' NAME LoopCount? '}}' TemplateContent '{{/' NAME '}}'
TriggerType   ::= 'ALWAYS' | 'AFTER_ANSWER' | 'ON_REFUSAL' | 'ON_ERROR' | 'CONDITIONAL' '(' CONDITION ')'
CATEGORY      ::= 'IN_CONTEXT_LEARNING' | 'REASONING' | 'OUTPUT_CONTROL' | 'META_DIRECTIVES' | 'CONTEXT_CONTROL'
NAME          ::= [a-zA-Z_][a-zA-Z0-9_]*
```

## Worked Examples

### Recipe

~~~promptspec
pattern Recipe
category OUTPUT_CONTROL

variables {
    pronoun? : enum = "I" | ["I", "You", "We"]
    goal* : string
    steps... : list
    complete? : bool = true
    missing? : bool = true
    unnecessary? : bool = false
}

template ```
{{pronoun}} would like to achieve {{goal}}.
{{#complete}}
Provide a complete sequence of steps.
{{/complete}}
{{#missing}}
Fill in any missing steps.
{{/missing}}
{{#unnecessary}}
Identify any unnecessary steps.
{{/unnecessary}}
{{#steps}}
Steps to consider:
{{^steps}}
  - {{.}}
{{/steps}}
{{/steps}}```
~~~

### FewShot

~~~promptspec
pattern FewShot
category IN_CONTEXT_LEARNING

variables {
    task* : string              "Description of the task"
    examples+ : list            "List of example objects"
    num_examples? : int = 3     "How many examples to show"
    selection? : enum = "first" | ["first", "random", "all"]
}

template ```
Task: {{task}}

Here are some examples:
{{^examples num_examples}}
Input: {{input}}
Output: {{output}}
{{/examples}}

Now do the same for:
```
~~~

### Reflection

~~~promptspec
pattern Reflection
category OUTPUT_CONTROL

variables {
    trigger? : enum = "AFTER_ANSWER" | ["ALWAYS", "AFTER_ANSWER"]
    explain? : bool = true             "Explain reasoning"
    assumptions? : bool = true         "State assumptions"
    improvements? : bool = false       "Suggest improvements"
}

trigger AFTER_ANSWER

template ```
{{#trigger}}
After generating your answer:
{{/trigger}}
{{#explain}}
Explain the reasoning behind your answer.
{{/explain}}
{{#assumptions}}
State any assumptions you made.
{{/assumptions}}
{{#improvements}}
Suggest potential improvements.
{{/improvements}}
```
~~~
