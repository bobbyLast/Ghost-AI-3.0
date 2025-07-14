"""
Ghost AI REST API: Exposes endpoints for tickets, performance, config, approvals, and ChatGPT data pulls.
"""
from fastapi import FastAPI, Body
from typing import List, Dict, Any
from odds_reverse_engineering.utils.chatgpt_data_fetcher import ChatGPTDataFetcher
from moneyline_ticket_generator import MoneylineTicketGenerator
from core.data.data_fetcher import DataFetcher
from ghost_ai_core_memory.ghost_brain import create_ghost_brain
from pathlib import Path

app = FastAPI()

# --- In-memory stubs for demo (replace with real GhostBrain integration) ---
tickets_memory = {"pending": [], "posted": [], "graded": []}
performance_memory = {}
self_awareness_memory = {}
config_memory = {"features": {}}
adaptation_logs = []

chatgpt_fetcher = ChatGPTDataFetcher()
moneyline_gen = MoneylineTicketGenerator()
data_fetcher = DataFetcher()
ghost_brain = create_ghost_brain(Path("ghost_ai_core_memory"))

@app.get("/tickets")
def get_tickets():
    """Return all tickets (pending, posted, graded)."""
    return tickets_memory

@app.post("/generate-tickets")
def generate_tickets(sport: str = Body(...), date: str = Body(None)):
    """Generate tickets for any sport (MLB, WNBA, tennis, golf, etc)."""
    try:
        tickets = moneyline_gen.generate_tickets(sport, date)
        return {"status": "ok", "tickets": tickets}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/performance")
def get_performance():
    """Return performance tracking from GhostBrain."""
    try:
        return {"status": "ok", "performance": ghost_brain.self_awareness.get("recent_performance", {})}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/self-awareness")
def get_self_awareness():
    """Return self-awareness/feature status from GhostBrain."""
    try:
        return {"status": "ok", "self_awareness": ghost_brain.self_awareness}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/config")
def get_config():
    """Return config (features, etc)."""
    try:
        return {"status": "ok", "config": config_memory}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/approve")
def approve_post(ticket_id: str = Body(...)):
    """Approve a ticket for posting (stub)."""
    # Implement real approval logic
    return {"status": "approved", "ticket_id": ticket_id}

@app.post("/decline")
def decline_post(ticket_id: str = Body(...)):
    """Decline a ticket for posting (stub)."""
    # Implement real decline logic
    return {"status": "declined", "ticket_id": ticket_id}

@app.post("/chatgpt-data")
def chatgpt_data(query: str = Body(...)):
    """Call ChatGPT for custom data pulls (news, context, stats, etc)."""
    try:
        result = chatgpt_fetcher._chatgpt_call(query)
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)} 