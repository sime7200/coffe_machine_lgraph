import json
import threading
from typing import Tuple, Dict, Any, Optional
from memory import log_order

_inventory_lock = threading.Lock()
INVENTORY_FILE = "data/inventory.json"

def load_inventory() -> Dict[str,int]:
    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)

def save_inventory(inv: Dict[str,int]):
    with open(INVENTORY_FILE, "w") as f:
        json.dump(inv, f, indent=2)

def check_inventory(order: Dict[str,Any]) -> Tuple[bool, str]:
    inv = load_inventory()
    drink = order.get("drink", "espresso")
    if inv.get(drink, 0) > 0:
        return True, f"Tutto ok, preparo un {drink}."
    else:
        return False, f"Mi dispiace, non ho più {drink}."

def decrement_inventory_atomic(order: Dict[str,Any]) -> bool:
    """Prova a decrementare l'inventario in modo atomic; ritorna True se avvenuto."""
    drink = order.get("drink", "espresso")
    with _inventory_lock:
        inv = load_inventory()
        if inv.get(drink, 0) > 0:
            inv[drink] -= 1
            save_inventory(inv)
            return True
        else:
            return False

def brew_coffee(order: Dict[str,Any], user_id: Optional[str] = None) -> str:
    # Log ordine
    log_order(user_id, order)
    return f"☕ Il tuo {order['drink']} {order['size']} è pronto! (zucchero: {order['sugar']}, temperatura: {order['temperature']})"

# tool to reply with possible drinks to order
# def get_available_drinks_old() -> Dict[str, int]:
#     inv = load_inventory()
#     list = []
#     try:
#         for drink, qty in inv.items():
#             list.append((drink, qty))
#         return dict(list)  # return as a dict
#     except Exception:
#         print("Errore nel leggere l'inventario")
#         return {}
    
# return a list of strings
def get_available_drinks() -> list:
    inv = load_inventory()
    list = []
    try:
        for drink, qty in inv.items():
            if qty > 0:
                list.append((drink, qty))
        return list  
    except Exception:
        print("Errore nel leggere l'inventario")
        return {}