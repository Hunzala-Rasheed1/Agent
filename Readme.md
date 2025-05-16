# LLM-Powered GraphQL Agent

This project is a small Python application that translates natural language queries into GraphQL requests against a Jobs API. It uses LangChain and OpenAI to understand the natural language and generate appropriate GraphQL queries, returning the results in human-readable text via a simple HTTP endpoint.

## Features

- Translates natural language questions into GraphQL queries
- Executes queries against a GraphQL API
- Returns human-readable responses
- Packaged as a Docker container using Azure-supported base image
- Logging of GraphQL queries for debugging and monitoring

## Prerequisites

- Python 3.9+
- Docker
- OpenAI API key
- GraphQL API endpoint

## Setup & Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/Hunzala-Rasheed1/Agent.git
   cd llm-graphql-agent
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials (use `.env.example` as a template):
   ```bash
   cp .env.example .env
   # Edit the .env file with your actual credentials
   ```

### How to Run Locally

1. Make sure your virtual environment is activated and `.env` file is set up.

2. Run the application:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. The API will be available at `http://localhost:8000`

### How to Build & Run the Docker Container

1. Build the Docker image:
   ```bash
   docker build -t llm-graphql-agent .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env llm-graphql-agent
   ```

3. The API will be available at `http://localhost:8000`

## API Usage

The API exposes a single endpoint for querying:

### POST /query

Process a natural language query and return an answer.

**Request Format:**
```json
{
  "q": "your question here"
}
```

**Response Format:**
```json
{
  "answer": "human-readable answer",
  "graphql_query": "the generated GraphQL query",
  "error": "error message if applicable"
}
```

## Example Requests & Responses

### Example 1: Basic Query

**Request:**
```json
{
  "q": "What job positions are available?"
}
```

**Response:**
```json
{
  "answer": "There are several job positions available. They include Software Engineer, Data Scientist, Product Manager, UI/UX Designer, DevOps Engineer, and QA Engineer. These positions are across different locations and have various requirements.",
  "graphql_query": "{\n  jobs {\n    title\n    location\n    department\n  }\n}"
}
```

### Example 2: Filtered Query

**Request:**
```json
{
  "q": "Are there any software engineering jobs in Seattle?"
}
```

**Response:**
```json
{
  "answer": "Yes, there are 2 software engineering positions available in Seattle. One is for a Senior Software Engineer that requires 5+ years of experience, and the other is for a Software Engineer II requiring 3+ years of experience.",
  "graphql_query": "{\n  jobs(where: { title_contains: \"Software Engineer\", location: \"Seattle\" }) {\n    id\n    title\n    description\n    requirements\n    location\n  }\n}"
}
```

## Configuration

For Azure OpenAI integration, update your `.env` file with the following:

```
OPENAI_API_KEY=
OPENAI_API_VERSION=
OPENAI_API_ENDPOINT=
GRAPHQL_API_URL=
```

## Troubleshooting

- **Error: Missing environment variables** - Make sure all required environment variables are set in your `.env` file.
- **GraphQL query errors** - Check the logs for the exact GraphQL query that was generated. It may need adjustments in the prompt templates.
- **API connection issues** - Verify that the GraphQL API endpoint is accessible from your environment.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
