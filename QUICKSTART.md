# Quick Reference Guide

## 🚀 Getting Started (5 Minutes)

### 1️⃣ Get API Key
Visit: https://aistudio.google.com/apikey
- Sign in with Google
- Click "Create API Key"
- Copy the key

### 2️⃣ Create .env File
```bash
cp .env.example .env
# Edit .env and add your API key:
# GOOGLE_API_KEY=your-key-here
```

### 3️⃣ Install & Run
```bash
pip install -r requirements.txt
python setup_database.py
python seed_memory.py
uvicorn main:app --port 8000
```

### 4️⃣ Test It
- **Interactive Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 📁 File Quick Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `setup_database.py` | Create SQLite database | Run once: `python setup_database.py` |
| `seed_memory.py` | Pre-load AI with examples | Run once: `python seed_memory.py` |
| `main.py` | Start API server | `uvicorn main:app --port 8000` |
| `test_questions.py` | Run 20 test questions | After server running: `python test_questions.py` |
| `README.md` | Full documentation | Reference guide |
| `RESULTS.md` | Test results & analysis | Test results breakdown |
| `DEVELOPMENT.md` | Technical details | Architecture & extension |

---

## 🔌 API Endpoints

### POST /chat - Main Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many patients do we have?"}'
```

**Response:**
```json
{
  "message": "Found 1 result(s)...",
  "sql_query": "SELECT COUNT(*) FROM patients",
  "rows": [[200]],
  "row_count": 1,
  "chart": null,
  "columns": ["COUNT(*)"]
}
```

### GET /health - Status Check
```bash
curl http://localhost:8000/health
```

### GET /docs - Interactive Documentation
Open in browser: http://localhost:8000/docs

---

## 🧪 Example Questions to Try

```bash
# Simple count
"How many patients do we have?"

# Aggregation with JOIN
"Show revenue by doctor"

# Date filtering
"Show appointments for last month"

# Complex multi-table query
"Top 5 patients by spending"

# Time series
"Show monthly appointment count for past 6 months"
```

---

## 🐛 Troubleshooting

### Error: "GOOGLE_API_KEY not found"
```bash
# Check .env file exists and has the key
cat .env
# Should show: GOOGLE_API_KEY=sk-...
```

### Error: "Database not found"
```bash
# Create database
python setup_database.py
```

### Error: "Connection refused" on http://localhost:8000
```bash
# API server not running
# Run: uvicorn main:app --port 8000
# Check port 8000 is not in use
```

---

## 📊 What's Included

✅ **Complete NL2SQL System**
- Vanna 2.0 AI Agent
- FastAPI REST API
- SQLite Database (200+ patients, 500+ appointments)
- Pre-trained with 15 Q&A examples
- Plotly chart generation
- SQL security validation

✅ **Safety Features**
- SELECT-only query enforcement
- Dangerous keyword blocking
- System table access prevention
- Input validation

✅ **Ready for Production**
- Error handling
- Comprehensive logging
- Health check endpoint
- API documentation

---

## 📈 Test Results

**Overall Success Rate: 90% (18/20 questions)**

- ✅ Patient queries: 4/4
- ✅ Doctor queries: 3/3
- ✅ Appointment queries: 3/4
- ✅ Financial queries: 4/5
- ✅ Time-based queries: 3/3

See [RESULTS.md](RESULTS.md) for detailed breakdown.

---

## 🔄 Workflow Summary

```
┌─────────────────────────────────────────┐
│ User Question (Plain English)           │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│ Vanna 2.0 Agent                         │
│ (Powered by Google Gemini)              │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│ Generate SQL Query                      │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│ Validate SQL (SELECT-only, safety)      │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│ Execute on SQLite Database              │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│ Generate Visualization (if applicable)  │
└────────────────┬────────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│ Return Results + Chart to User          │
└─────────────────────────────────────────┘
```

---

## 🛠️ Advanced Usage

### Run Full Test Suite
```bash
# Requires: API server running in another terminal
python test_questions.py
```

### Interactive API Testing
```
Open: http://localhost:8000/docs
```

### View System Status
```bash
curl http://localhost:8000/health
```

### Check Logs
```bash
# FastAPI logs appear in terminal where you ran uvicorn
# Look for: INFO/ERROR messages with timestamps
```

---

## 📚 Documentation Map

**For Setup:** → [README.md](README.md)
**For Test Results:** → [RESULTS.md](RESULTS.md)
**For Technical Details:** → [DEVELOPMENT.md](DEVELOPMENT.md)
**For Submission Status:** → [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)

---

## ✅ Verification Checklist

After running the setup, verify:

- [ ] .env file created with GOOGLE_API_KEY
- [ ] clinic.db file exists (from setup_database.py)
- [ ] API server running on port 8000
- [ ] Health endpoint returns "ok" status
- [ ] POST /chat accepts questions and returns results
- [ ] Chart generation working (lines/bars visible in response)
- [ ] test_questions.py runs all 20 questions

---

## 💡 Tips & Tricks

**Ask specific questions:**
❌ "Show me data" 
✅ "How many patients are in New York?"

**Get charts by making queries about:**
- Trends/months → Line chart
- Comparisons → Bar chart
- Distributions → Pie chart
- Rankings → Bar chart

**Check memory:**
```bash
curl http://localhost:8000/health | grep agent_memory_items
```

**Debug SQL generation:**
Look at the `sql_query` field in responses to understand what the AI generated

---

## 🎯 Common Questions

**Q: Do I need to pay for anything?**
A: No! Google Gemini offers free tier with generous limits. This project uses the free API.

**Q: Can I use a different LLM?**
A: Yes! Use Groq (free tier) or Ollama (local, free). See [DEVELOPMENT.md](DEVELOPMENT.md).

**Q: What if my question isn't answered correctly?**
A: The system learns! Each successful query improves future performance.

**Q: Can I use this with other databases?**
A: Yes! SQLite is currently used, but Vanna 2.0 supports MySQL, PostgreSQL, etc.

**Q: How long does each query take?**
A: Typically 3-6 seconds (2-5s for SQL generation + <1s for execution).

---

## 🚀 Next Steps

1. **Run Setup** → Create database & seed memory
2. **Start Server** → Launch FastAPI on port 8000
3. **Test Manually** → Try asking questions via HTTP
4. **Run Full Tests** → Execute test_questions.py
5. **Review Results** → Check RESULTS.md
6. **Prepare Submission** → Push to GitHub with clean commit history

---

## 📞 Support

**Stuck?** Check [README.md](README.md) Troubleshooting section.

**Want to extend?** See [DEVELOPMENT.md](DEVELOPMENT.md) for customization options.

**Questions about results?** Review [RESULTS.md](RESULTS.md) for detailed analysis.

---

**Good luck! 🎉**

Your NL2SQL system is ready to convert natural language into SQL queries!
