import os
from typing import TypedDict, Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.config import RunnableConfig

import database  # Подключаем нашу базу данных!

# 1. Pydantic-схема для гарантированного ответа от LLM
class TradingStrategy(BaseModel):
    action: Literal["buy", "sell", "hold"] = Field(description="Торговое действие")
    confidence: int = Field(description="Уровень уверенности от 0 до 100")
    reasoning: str = Field(description="Подробное обоснование решения на русском языке")

# Инициализация LLM с принудительной структурой ответа
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = llm.with_structured_output(TradingStrategy)

# 2. ИСПРАВЛЕННОЕ СОСТОЯНИЕ (AgentState)
class AgentState(TypedDict):
    weather_data: Dict[str, Any]
    strategy: Any       # Изменили имя ключа для совместимости с main.py
    status: str         # Добавили status, чтобы LangGraph разрешил его обновлять

def weather_analyst_node(state: AgentState) -> Dict[str, Any]:
    weather = state["weather_data"]

    prompt = f"""
    Ты — главный AI-трейдер энергии в микросети. Прими торговое решение на основе погодных условий.

    ЧЕТКИЕ ПРАВИЛА ТОРГОВЛИ:
    1. Если скорость ветра > 5 m/s ИЛИ температура > 25°C — у нас ИЗБЫТОК генерации (ветряки и солнце работают на максимум). 
       Твое решение: "sell" (продать энергию в сеть). Уверенность: 85-95%.
    2. Если облачность > 70% И скорость ветра < 3 m/s — у нас ДЕФИЦИТ генерации. 
       Твое решение: "buy" (докупить энергию). Уверенность: 85-95%.
    3. В остальных умеренных случаях — решение: "hold". Уверенность: 60-75%.

    ТЕКУЩИЕ МЕТРИКИ ПОГОДЫ:
    - Температура: {weather.get('temperature')}°C
    - Скорость ветра: {weather.get('wind_speed')} m/s
    - Облачность: {weather.get('cloud_cover')}%
    - Влажность: {weather.get('humidity')}%
    """

    result: TradingStrategy = structured_llm.invoke(prompt)
    return {"strategy": result, "status": "analyzed"}

# Функция-маршрутизатор (Risk Policy Router)
def route_trade(state: AgentState) -> str:
    strategy = state.get("strategy")
    # Берем уверенность напрямую из объекта
    confidence = strategy.confidence if strategy else 0

    if confidence >= 80:
        return "executor"
    
    return "human_approval"

def human_approval_node(state: AgentState) -> Dict[str, Any]:
    # Теперь мы возвращаем разрешенный ключ status, чтобы избежать InvalidUpdateError
    return {"status": "human_approved"}

# 3. АСИНХРОННАЯ НОДА ИСПОЛНЕНИЯ (Сохраняет в базу!)
async def execute_trade_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    # Достаем ID текущей сессии (нити)
    thread_id = config["configurable"]["thread_id"]
    strategy = state.get("strategy")
    
    if strategy:
        # Сохраняем реальное решение ИИ в PostgreSQL!
        await database.save_trading_decision(
            thread_id=thread_id,
            action=strategy.action,
            decision_data=strategy.model_dump()
        )
        
    return {"status": "executed"}

# Сборка графа
builder = StateGraph(AgentState)

builder.add_node("analyst", weather_analyst_node)
builder.add_node("human_approval", human_approval_node)
builder.add_node("executor", execute_trade_node)

builder.set_entry_point("analyst")

builder.add_conditional_edges(
    "analyst",
    route_trade,
    {
        "executor": "executor",
        "human_approval": "human_approval"
    }
)

builder.add_edge("human_approval", "executor")
builder.add_edge("executor", END)

memory = MemorySaver()
app_graph = builder.compile(
    checkpointer=memory, 
    interrupt_before=["human_approval"]
)