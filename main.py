"""
FastAPI Application for NL2SQL System
Exposes REST API endpoints for natural language to SQL conversion and execution
VERSION: 2.0 (Updated with Agent LLM Service & Tool Registry integration)
"""

import re
import logging
import sqlite3
import traceback
from typing import Optional, Any, Dict, List
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from vanna_setup import get_agent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NL2SQL Chat API",
    description="AI-Powered Natural Language to SQL Conversion",
    version="1.0.0"
)

# Global agent instance
try:
    agent = get_agent()
    logger.info("✓ Vanna Agent initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize agent: {e}")
    agent = None


# ============================================================================
# Pydantic Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(..., min_length=1, max_length=1000, description="User's natural language question")


class ChartData(BaseModel):
    """Chart data model"""
    type: str
    data: List[Dict[str, Any]]
    layout: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str
    sql_query: str
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    chart: Optional[Dict[str, Any]] = None
    chart_type: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    agent_memory_items: int
    timestamp: str


# ============================================================================
# SQL Validation
# ============================================================================

class SQLValidator:
    """Validates SQL queries for safety"""
    
    # Dangerous patterns that should be rejected
    DANGEROUS_KEYWORDS = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'EXEC',
        'xp_', 'sp_', 'GRANT', 'REVOKE', 'SHUTDOWN', 'PRAGMA'
    ]
    
    DANGEROUS_TABLES = [
        'sqlite_master', 'sqlite_temp_master', 'sqlite_sequence',
        'information_schema'
    ]
    
    @staticmethod
    def validate(sql: str) -> tuple[bool, Optional[str]]:
        """
        Validate SQL query
        """
        if not sql or not sql.strip():
            return False, "SQL query is empty"
        
        sql_upper = sql.upper().strip()
        
        # Check if it starts with SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Check for dangerous keywords
        for keyword in SQLValidator.DANGEROUS_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                return False, f"Dangerous keyword '{keyword}' detected"
        
        # Check for system tables
        for table in SQLValidator.DANGEROUS_TABLES:
            if table.lower() in sql.lower():
                return False, f"Access to system table '{table}' is not allowed"
        
        # Check for comments
        if '--' in sql or '/*' in sql:
            return False, "SQL comments are not allowed"
        
        return True, None


# ============================================================================
# Chart Generation
# ============================================================================

def generate_chart(df: pd.DataFrame, question: str) -> tuple[Optional[Dict], Optional[str]]:
    """
    Attempt to generate appropriate chart based on data
    """
    try:
        if df.empty or len(df.columns) < 2:
            return None, None
        
        question_lower = question.lower()
        
        # Rule-based chart selection
        if any(word in question_lower for word in ['revenue', 'cost', 'amount', 'total']):
            if 'by' in question_lower or len(df) > 1:
                x_col = df.columns[0]
                y_col = df.columns[1] if len(df.columns) > 1 else None
                if y_col:
                    fig = px.bar(df, x=x_col, y=y_col, title="Financial Data Distribution")
                    return fig.to_dict(), "bar"
        
        elif any(word in question_lower for word in ['trend', 'month', 'time', 'year', 'daily']):
            if len(df.columns) >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]
                fig = px.line(df, x=x_col, y=y_col, markers=True, title="Trend Over Time")
                return fig.to_dict(), "line"
        
        elif any(word in question_lower for word in ['top', 'count', 'highest', 'most']):
            if len(df) > 1 and len(df.columns) >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]
                fig = px.bar(df, x=x_col, y=y_col, title="Rankings/Counts")
                return fig.to_dict(), "bar"
        
        elif any(word in question_lower for word in ['percentage', 'distribution', 'ratio', 'share']):
            if len(df.columns) >= 2:
                fig = px.pie(df, values=df.columns[1], names=df.columns[0], title="Proportional Distribution")
                return fig.to_dict(), "pie"
        
        # Default fallback
        if len(df.columns) >= 2:
            fig = px.line(df, title="Query Results Visualization")
            return fig.to_dict(), "line"
        
        return None, None
        
    except Exception as e:
        logger.debug(f"Chart generation failed: {e}")
        return None, None


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process natural language question and return SQL results
    """
    try:
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent not initialized"
            )
        
        question = request.question.strip()
        logger.info(f"Processing question: {question[:100]}")
        
        # Input validation
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # 1. Generate SQL using Vanna 2.0 Service-Oriented approach
        try:
            # Vanna 2.0 Agent doesn't have .generate_sql(), its llm_service does.
            sql_query = agent.llm_service.generate_sql(
                question=question, 
                catalog=agent.agent_memory.get_all_mappings()
            )
        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate SQL: {str(e)[:100]}"
            )
        
        if not sql_query or not sql_query.strip():
            raise HTTPException(status_code=500, detail="Agent generated empty SQL query")
        
        logger.info(f"Generated SQL: {sql_query[:100]}")
        
        # 2. Validate SQL for safety
        is_valid, error_msg = SQLValidator.validate(sql_query)
        if not is_valid:
            logger.warning(f"SQL validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=f"SQL validation failed: {error_msg}")
        
        # 3. Execute SQL using registered Tools
        try:
            # We fetch the tool registered in vanna_setup.py
            sql_tool = agent.tool_registry.get_tool("run_sql")
            result_df = sql_tool.run(sql=sql_query)
            
            if result_df is None:
                result_df = pd.DataFrame()
            
            logger.info(f"Query executed successfully, rows: {len(result_df)}")
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Database execution error: {str(e)[:100]}"
            )
        
        # 4. Prepare response data
        if result_df.empty:
            columns = []
            rows = []
            summary_message = "No data found matching your query."
            chart_dict, chart_type = None, None
        else:
            columns = result_df.columns.tolist()
            rows = result_df.values.tolist()
            
            # Generate summary message
            summary_message = f"Found {len(result_df)} result(s). "
            if len(result_df.columns) >= 2:
                first_col = result_df.columns[0]
                second_col = result_df.columns[1]
                summary_message += f"Top result: {first_col}={result_df.iloc[0, 0]}, {second_col}={result_df.iloc[0, 1]}"
            
            # Generate chart
            chart_dict, chart_type = generate_chart(result_df, question)
        
        return ChatResponse(
            message=summary_message,
            sql_query=sql_query,
            columns=columns,
            rows=rows,
            row_count=len(rows),
            chart=chart_dict,
            chart_type=chart_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)[:100]}"
        )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Comprehensive Health check endpoint
    """
    try:
        agent_ok = agent is not None
        db_ok = False
        memory_count = 0
        
        # Check database connection
        try:
            from pathlib import Path
            db_path = Path(__file__).parent / "clinic.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            db_ok = True
            conn.close()
        except:
            db_ok = False
        
        # Get memory items count (Vanna 2.0 path)
        try:
            if agent and hasattr(agent.agent_memory, 'get_all_mappings'):
                memory_count = len(agent.agent_memory.get_all_mappings())
        except:
            memory_count = 0
        
        return HealthResponse(
            status="ok" if (agent_ok and db_ok) else "degraded",
            database="connected" if db_ok else "disconnected",
            agent_memory_items=memory_count,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(status="error", database="unknown", agent_memory_items=0, timestamp=datetime.now().isoformat())


@app.get("/")
async def root():
    return {
        "name": "NL2SQL Chat API",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Natural Language to SQL",
            "GET /health": "System status",
            "GET /docs": "API Docs"
        }
    }


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status": "error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status": "error"}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")