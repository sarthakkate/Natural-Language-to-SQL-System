# Development Guide

## Project Structure

```
congin/
├── Core Application Files
│   ├── main.py                 # FastAPI application (REST API)
│   ├── vanna_setup.py          # Vanna 2.0 Agent initialization
│   ├── setup_database.py       # Database creation script
│   ├── seed_memory.py          # Agent memory seeding
│   └── test_questions.py       # Integration test runner
│
├── Configuration Files
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   └── .gitignore              # Git ignore rules
│
├── Documentation
│   ├── README.md               # Main documentation
│   ├── RESULTS.md              # Test results & analysis
│   └── DEVELOPMENT.md          # This file
│
├── Setup Scripts
│   ├── quickstart.bat          # Windows setup script
│   └── quickstart.sh           # Unix/Linux/Mac setup script
│
└── Generated Files (after setup)
    ├── clinic.db               # SQLite database
    └── test_results.json       # Test execution results
```

## File Responsibilities

### main.py
**FastAPI REST API Application**

Key Components:
- **ChatRequest/ChatResponse Models** - Pydantic validation
- **SQLValidator** - Security validation (SELECT-only enforcement)
- **Chart Generation** - Plotly visualization logic
- **Endpoints**:
  - `POST /chat` - Main NL2SQL endpoint
  - `GET /health` - Health status check
  - `GET /` - API info

Key Functions:
```python
async def chat(request: ChatRequest) -> ChatResponse
async def health() -> HealthResponse
```

Error Handling:
- HTTP Exception Handler - Returns proper status codes
- General Exception Handler - Comprehensive logging
- SQL Validation Errors - Friendly error messages

### vanna_setup.py
**Vanna 2.0 Agent Configuration**

Responsibilities:
- Create GeminiLlmService with API key
- Initialize ToolRegistry with 4 Vanna tools
- Create DemoAgentMemory for learning
- Configure SqliteRunner for database access
- Define UserResolver for user identification
- Assemble all components into Agent

Export:
```python
def get_agent() -> Agent
```

### setup_database.py
**Database Schema & Data Generation**

Schema Tables:
1. **patients** (200 records)
2. **doctors** (15 records)
3. **appointments** (500 records)
4. **treatments** (350 records)
5. **invoices** (300 records)

Data Generation Strategy:
- Realistic names from predefined lists
- Date spread across 12 months
- Realistic cost ranges ($50-$5000)
- Mixed appointment statuses
- Realistic invoice payment states

### seed_memory.py
**Agent Memory Pre-seeding**

Pre-loads 15 Q&A pairs covering:
- Patient queries (4 examples)
- Doctor queries (3 examples)
- Appointment queries (3 examples)
- Financial queries (3 examples)
- Time-based queries (2 examples)

Method:
```python
agent.memory.store_question_sql_mapping(question, sql)
```

## Code Architecture

### Request Flow

```
1. User sends question to POST /chat endpoint
   ↓
2. Input Validation
   - Check if question is empty
   - Verify length ≤ 1000 chars
   ↓
3. SQL Generation
   - Call agent.generate_sql(question)
   - Vanna uses Gemini LLM + memory
   ↓
4. SQL Validation
   - Check for dangerous keywords
   - Verify SELECT-only query
   - Block system table access
   ↓
5. Query Execution
   - Execute on SQLite via agent.run_sql()
   - Return DataFrame with results
   ↓
6. Chart Generation
   - Analyze query type and data
   - Generate Plotly visualization
   ↓
7. Response Formatting
   - Build ChatResponse object
   - Include SQL, rows, columns, chart
   ↓
8. Return JSON to client
```

### Error Handling Layers

```
Layer 1: Input Validation (main.py)
  - Empty/too long questions

Layer 2: SQL Validation (SQLValidator)
  - Dangerous keywords
  - System table access

Layer 3: Execution Error Handling
  - Database errors
  - SQL syntax errors
  - API errors from Gemini

Layer 4: Global Exception Handler
  - Catches uncaught exceptions
  - Logs for debugging
```

## Configuration & Customization

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=<your-gemini-api-key>

# Optional (not currently used)
# DATABASE_PATH=<path-to-db>
# API_PORT=8000
# LOG_LEVEL=INFO
```

### Vanna 2.0 Components

**LLM Service Options:**

Option A (Current): Google Gemini
```python
from vanna.integrations.google import GeminiLlmService
llm = GeminiLlmService(api_key=key, model="gemini-2.5-flash")
```

Option B: Groq LLaMA
```python
from vanna.integrations.openai import OpenAILlmService
llm = OpenAILlmService(
    api_key=key,
    model="llama-3.3-70b",
    base_url="https://api.groq.com/openai/v1"
)
```

Option C: Ollama (Local)
```python
from vanna.integrations.openai import OpenAILlmService
llm = OpenAILlmService(
    api_key="ollama",
    model="llama3",
    base_url="http://localhost:11434/v1"
)
```

**Tool Registry:**

Current tools:
- `RunSqlTool` - Execute SQL queries
- `VisualizeDataTool` - Create visualizations
- `SaveQuestionToolArgsTool` - Save successful patterns
- `SearchSavedCorrectToolUsesTool` - Retrieve learned patterns

To add new tools:
```python
from vanna.tools import CustomTool

class MyCustomTool(CustomTool):
    def execute(self, *args, **kwargs):
        # Implementation
        pass

registry.register(MyCustomTool)
```

### Database Customization

To use a different database:

1. Change SqliteRunner to appropriate runner:
```python
from vanna.integrations.mysql import MySQLRunner
sql_runner = MySQLRunner(connection="mysql://user:pass@host/db")
```

2. Update schema in setup_database.py

3. Update dummy data generation

## Testing & Validation

### Unit Testing (Manual)

```bash
# Test individual components
python -c "from vanna_setup import get_agent; agent = get_agent(); print('✓ Agent OK')"

# Test database
python -c "import sqlite3; conn = sqlite3.connect('clinic.db'); print(conn.execute('SELECT COUNT(*) FROM patients').fetchone())"
```

### Integration Testing

```bash
# Run test suite (requires API running)
python test_questions.py

# This runs 20 predefined questions and reports:
# - Success rate
# - Response times
# - SQL queries generated
# - Failed questions
```

### API Testing

Using FastAPI's interactive docs:
```
http://localhost:8000/docs
```

Or using curl:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many patients?"}'
```

## Performance Optimization

### Current Bottlenecks

1. **SQL Generation** (2-5s)
   - Gemini API latency
   - Complex reasoning required

2. **Multi-table Joins** (0.5-1s)
   - No query optimization
   - No indexes

3. **Large Result Sets** (+ time proportional to size)
   - All data returned
   - No pagination

### Optimization Strategies

#### Short-term
```python
# 1. Add Query Caching
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_generate_sql(question):
    return agent.generate_sql(question)

# 2. Add Result Pagination
def get_page(df, page=1, page_size=1000):
    return df.iloc[page*page_size:(page+1)*page_size]

# 3. Add Indexes to Database
cursor.execute("CREATE INDEX idx_patient_city ON patients(city)")
cursor.execute("CREATE INDEX idx_appt_status ON appointments(status)")
```

#### Long-term
```python
# 1. Use Connection Pool
from vanna.integrations.sqlite import SqliteRunner
runner = SqliteRunner(connection=db_path, pool_size=5)

# 2. Implement Redis Caching
from redis import Redis
cache = Redis(host='localhost', port=6379)

# 3. Add Query Execution Plan Analysis
EXPLAIN_QUERY_PLAN statement before running
```

## Debugging

### Enable Detailed Logging

```python
# In main.py
logging.basicConfig(level=logging.DEBUG)

# Or via environment
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
```

### Common Issues

**Issue: "GOOGLE_API_KEY not found"**
```bash
# Solution: Check .env file exists
cat .env
# Should show: GOOGLE_API_KEY=sk-...

# Or verify
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

**Issue: "Database not found"**
```bash
# Solution: Run setup
python setup_database.py

# Verify
ls -la clinic.db
```

**Issue: "SQL validation error"**
```python
# Check what SQL was generated
# In response: check "sql_query" field
# Verify it's a valid SELECT query

# Add debug logging
from main import SQLValidator
is_valid, error = SQLValidator.validate(sql)
print(f"Valid: {is_valid}, Error: {error}")
```

## Extending the System

### Adding New Endpoints

```python
from fastapi import FastAPI

@app.post("/query-history")
async def get_query_history(limit: int = 10):
    """Get recently executed queries"""
    # Implementation
    pass

@app.get("/stats")
async def get_statistics():
    """Get system statistics"""
    # Implementation
    pass
```

### Adding Custom Validators

```python
class CustomSQLValidator:
    @staticmethod
    def validate_performance(sql: str):
        """Check for performance issues"""
        if "WHERE" not in sql.upper() and "LIMIT" not in sql.upper():
            return False, "Query should have WHERE or LIMIT"
        return True, None
```

### Adding Monitoring

```python
import time
from prometheus_client import Histogram

query_duration = Histogram('query_duration_seconds', 'Query execution time')

@query_duration.time()
async def monitored_chat(request: ChatRequest):
    # Automatically tracks timing
    pass
```

## Deployment Considerations

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Add request logging/monitoring
- [ ] Implement rate limiting
- [ ] Add query result caching
- [ ] Set up database backups
- [ ] Monitor API latency
- [ ] Implement alerting
- [ ] Use environment-specific configs
- [ ] Add health checks
- [ ] Document SLAs

### Scaling Strategies

1. **Horizontal**: Multiple API instances behind load balancer
2. **Vertical**: Larger database instance
3. **Caching**: Redis for queries & results
4. **Async**: Queue long-running queries
5. **CDN**: Cache chart generation

## References

- [Vanna 2.0 Documentation](https://vanna.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Plotly Python](https://plotly.com/python)
- [Google Gemini API](https://ai.google.dev)

---

**Last Updated:** January 2024
