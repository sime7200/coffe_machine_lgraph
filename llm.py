from langchain_mistralai import ChatMistralAI
import json
from typing import Optional, Dict, Any
from models import OrderModel
from collections import Counter
import time
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

llm = ChatMistralAI(
    model="open-mistral-7b",
    temperature=0.0, 
    api_key=api_key
)

PROMPT_TEMPLATE = """
Sei un barista digitale. Rispondi sempre SOLO con un JSON valido.

Regole:
- Se l'utente ordina un caffè → JSON con campo obbligatorio "action":"make_drink"
  Esempio: 
  {{"action":"make_drink","drink":"cappuccino","size":"grande","sugar":"no","temperature":"medio","extras":[]}}
- Se l'utente chiede la lista dei drink disponibili → JSON {{"action":"list_drinks"}}

Esempi:

Input: "Vorrei un cappuccino grande senza zucchero"
Output: {{"action":"make_drink","drink":"cappuccino","size":"grande","sugar":"no","temperature":"medio","extras":[]}}

Input: "Un espresso piccolo, caldo"
Output: {{"action":"make_drink","drink":"espresso","size":"piccolo","sugar":"no","temperature":"alto","extras":[]}}

Input: "I'd like a sweet tea"
Output: {{"action":"make_drink","drink":"tea","size":"medio","sugar":"yes","temperature":"alto","extras":[]}}

Input: "I'd like a juice"
Output: {{"action":"make_drink","drink":"juice","size":"medio","sugar":"no","temperature":"cold","extras":[]}}

Input: "Che drink ci sono?"
Output: {{"action":"list_drinks"}}

Input: "Che drink hai?"
Output: {{"action":"list_drinks"}}

Ora: {user_input}
"""

def parse_json_safe(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    # A volte LLM aggiunge ```json or text; clean it
    if text.startswith("```"):
        text = "\n".join(text.splitlines()[1:-1])
    # find first { and last }
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        snippet = text[start:end]
        return json.loads(snippet)
    except Exception:
        # fallback
        try:
            return json.loads(text)
        except Exception:
            return None

def interpret_order(user_input: str, tries: int = 5, pause: float = 0.3):
    # self-consistency: sample multiple times and pick modal response
    parses = []
    for i in range(tries):
        prompt = PROMPT_TEMPLATE.format(user_input=user_input)
        response = llm.invoke(prompt)  # wrapper used earlier
        parsed = parse_json_safe(response.content)
        # print("⚡ RAW response:", response.content)   # debug
        # print("📝 Parsed:", parsed)  
        if parsed:
            # caso speciale: action list_drinks
            if parsed.get("action") == "list_drinks":
                return parsed
            
            # fallback: se sembra un ordine ma manca action lo aggiungo io
            if "drink" in parsed and "size" in parsed:
                parsed["action"] = "make_drink"
            try:
                # validate with pydantic
                order = OrderModel(**parsed)
                # normalized dict
                parses.append(order.dict())
            except Exception:
                # invalid, ignore
                pass
        time.sleep(pause)
    if not parses:
        # print("⚠️ Nessun parse valido, ritorno None") # debug
        return None  # caller will ask for clarification
    # Self-consistency: choose the most common parse (mode)
    reprs = [json.dumps(p, sort_keys=True) for p in parses]
    most_common = Counter(reprs).most_common(1)[0][0]
    return json.loads(most_common)


def generate_reply(state: dict) -> str:
    prompt = f"""
    You are a friendly barista.
    Context state: {state}

    Rules:
    - Reply in natural English.
    - If state['parsed']['action'] == 'unknown', present yourself and politely say you only understand coffee-related requests.
    - If there is already a message in state (like inventory errors or confirmations), use it as base.
    - If there is a successful order, confirm warmly to the customer.
    - Do not return JSON, only natural sentences.
    """
    return llm.invoke(prompt).content
