from langchain.prompts import PromptTemplate

# Prompt for converting natural language to GraphQL
NL_TO_GRAPHQL_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template="""
You are an AI assistant specialized in converting natural language questions into GraphQL queries.

Given the GraphQL schema and a natural language question, generate a valid GraphQL query that will answer the question.

GraphQL Schema:
{schema}

User Question:
{question}

Follow these steps:
1. Analyze the question to understand what information the user is looking for
2. Identify relevant types and fields from the schema that could answer this question
3. Construct a valid GraphQL query that will retrieve the necessary information
4. For complex queries, include necessary arguments and filters
5. Only include fields that are relevant to the question

Return ONLY the GraphQL query without any additional explanation.
"""
)

# Prompt for answering with GraphQL results
ANSWER_PROMPT = PromptTemplate(
    input_variables=["question", "graphql_query", "result"],
    template="""
You are an AI assistant that helps users understand data from a Jobs API.

Original question: {question}

The following GraphQL query was executed:
```graphql
{graphql_query}
```

Result:
```json
{result}
```

Provide a clear, concise answer to the original question based on this data. Format the response in a human-readable way. 
If there were errors in the GraphQL query, explain what might have gone wrong in user-friendly terms.
"""
)