from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
import uuid

from models import WeatherData
import database
from graph import app_graph  # Import the compiled LangGraph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")
    await database.connect_db()
    yield
    logger.info("Shutting down FastAPI application...")
    await database.close_db()

app = FastAPI(title="Micro Energy Trader API", lifespan=lifespan)

# ---------------------------------------------------------
# Existing Ingest Endpoint
# ---------------------------------------------------------
@app.post("/api/v1/weather/ingest")
async def ingest_weather(data: WeatherData):
    try:
        # Преобразуем модель Pydantic в словарь
        weather_dict = data.model_dump()
        
        # Страховка: если из n8n пришел humidity вместо solar_irradiance
        if "solar_irradiance" not in weather_dict or weather_dict["solar_irradiance"] is None:
            weather_dict["solar_irradiance"] = weather_dict.get("humidity", 0.0)

        # Сохраняем в правильную схему базы данных
        await database.save_weather_data(weather_dict)
        logger.info("Successfully saved weather data to TimescaleDB.")
        
        # Автоматически запускаем AI-агента
        return await trigger_agent(data)
        
    except Exception as e:
        logger.error(f"Error ingesting data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal database error: {e}")

# ---------------------------------------------------------
# Multi-Agent & HITL Endpoints
# ---------------------------------------------------------
@app.post("/api/v1/agent/trigger")
async def trigger_agent(data: WeatherData):
    """Starts the LangGraph workflow and pauses before trade execution."""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initial state
    state_input = {
        "weather_data": data.model_dump(mode='json'),
        "status": "started"
    }
    
    # Run the graph (it will stop at 'interrupt_before=["execute_trade"]')
    await app_graph.ainvoke(state_input, config)
    
    # Fetch the state after interruption
    current_state = app_graph.get_state(config)
    
    return {
        "message": "Graph paused for Human-in-the-Loop (HITL) approval.",
        "thread_id": thread_id,
        "next_step": current_state.next,
        "strategy_proposed": current_state.values.get("strategy")
    }

@app.post("/api/v1/agent/approve/{thread_id}")
async def approve_trade(thread_id: str):
    """Resumes the paused graph to execute the trade."""
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if the thread exists and is paused
    state = app_graph.get_state(config)
    if not state.next:
        raise HTTPException(status_code=400, detail="No pending actions for this thread. Graph might already be finished.")
    
    # Resume the graph with a 'None' input (continues from paused state)
    await app_graph.ainvoke(None, config)
    
    # Get the final state
    final_state = app_graph.get_state(config)
    
    return {
        "message": "Trade execution approved and completed.",
        "thread_id": thread_id,
        "final_status": final_state.values.get("status"),
        "executed_strategy": final_state.values.get("strategy")
    }

@app.get("/api/v1/agent/approve-get/{thread_id}", response_class=HTMLResponse)
async def approve_trade_get(thread_id: str):
    """
    A GET wrapper for the approve endpoint to allow easy clicking from Telegram/Email.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if the thread exists and is paused
    state = app_graph.get_state(config)
    if not state.next:
        return HTMLResponse(content="<h3>No pending actions for this thread or graph already finished.</h3>", status_code=400)
    
    # Resume the graph
    await app_graph.ainvoke(None, config)
    final_state = app_graph.get_state(config)
    
    strategy = final_state.values.get("strategy")
    action = strategy.action if strategy else "Unknown"
    
    return HTMLResponse(content=f"""
    <html>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h2 style="color: green;">✅ Trade Approved Successfully!</h2>
            <p><strong>Thread ID:</strong> {thread_id}</p>
            <p><strong>Action Executed:</strong> {action.upper()}</p>
            <p>You can close this window.</p>
        </body>
    </html>
    """)