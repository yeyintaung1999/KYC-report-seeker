# KYC Report Seeker

KYC Report Seeker is an AI-powered tool for researching people and companies to identify potential risks from public information.

It uses Amazon Bedrock to analyze search results from Tavily and generates a structured KYC report with a risk score, summary, and source links. The results are validated using Pydantic.

## How It Works

1. Provide a person's and company's information.
2. Tavily searches the web for relevant information.
3. Amazon Bedrock analyzes the findings.
4. The agent generates a KYC report in JSON format.

## Requirements

- Python 3.14+
- AWS credentials with Amazon Bedrock access
- Tavily API key
- AWS permissions for AgentCore deployment

## Setup

Create a virtual environment and install dependencies:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```dotenv
AWS_REGION=ap-northeast-1
MODEL_ID=your-bedrock-model-id
TAVILY_API_KEY=your-tavily-api-key
```

Make sure your AWS credentials are configured and keep your `.env` file private.

## Run Locally

```bash
python -m app.main
```

The sample target is configured in `app/main.py`. Edit the `input_payload` to investigate someone else.

## Deploy to Amazon Bedrock AgentCore

Install the starter toolkit and run:

```bash
pip install bedrock-agentcore-starter-toolkit
python deploy.py
```

The deployment script sets up the AgentCore runtime using `app/agentcore_app.py`.

The agent accepts a prompt and an optional session ID:

```json
{
  "prompt": "Investigate Example Person at Example Company.",
  "session_id": "case-123"
}
```

## Project Structure

```text
app/
├── agentcore_app.py
├── main.py
├── schemas.py
├── client/
│   ├── bedrock_client.py
│   └── tavily_client.py
├── deepagent/
│   └── deep_agent.py
└── langgraph_agent/
    ├── prompt.py
    └── ...

deploy.py
requirements.txt
```

## Report Output

The report includes:

- Case ID and target information
- Risk score (0–100)
- Summary of adverse findings
- Source links and evidence scores
- Investigation status and completion time

The agent focuses on adverse information, removes duplicate sources, and returns an empty source list with a score of zero when no adverse findings are identified.

**Note:** Search results should always be reviewed to confirm the correct identity and verify the findings before making KYC or business decisions.