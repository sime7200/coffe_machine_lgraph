from langgraph.graph import StateGraph, END
from state import CoffeeState
from llm import interpret_order, generate_reply
from tools import check_inventory, brew_coffee, decrement_inventory_atomic, get_available_drinks
import memory


# Node 1: interpretazione ordine
def node_interpret(state: CoffeeState):
    parsed = interpret_order(state["order"])
    if not parsed:
        return {"parsed": {"action": "fallback"}}
    return {"parsed": parsed}

# Node 2
def node_check_inventory(state: CoffeeState):
    ok, msg = check_inventory(state["parsed"])
    return {"inventory_ok": ok, "message": msg}

# Node 3
def node_brew(state: CoffeeState):
    # Prova a decrementare l'inventario in modo atomic
    order = state["parsed"]
    if not decrement_inventory_atomic(order):
        return {"message": "Sembra che la disponibilità sia cambiata... riprova."}
    msg = brew_coffee(state["parsed"])
    return {"message": msg}

# Special node to list drinks
def node_list_drinks(state: CoffeeState):
    drinks = get_available_drinks()
    msg = "Attualmente posso preparare:\n" + "\n".join(f"- {d} ({q})" for d, q in drinks)
    return {"message": msg}

# Finale node for the final answer
def node_serve(state: CoffeeState):
    reply = generate_reply(state)
    return {"message": reply}


graph = StateGraph(CoffeeState)

graph.add_node("interpret", node_interpret)
graph.add_node("check_inventory", node_check_inventory)
graph.add_node("brew", node_brew)
graph.add_node("list_drinks", node_list_drinks)
graph.add_node("serve", node_serve)

graph.set_entry_point("interpret")

# Da check_inventory a, o brew o serve
graph.add_conditional_edges(
    "check_inventory",
    lambda s: "brew" if s["inventory_ok"] else "serve",
    {"brew": "brew", "serve": "serve"}
)


graph.add_conditional_edges(
    "interpret",
    lambda s: (
        "list_drinks"
        if s["parsed"].get("action") == "list_drinks"
        else "check_inventory"
        if s["parsed"].get("action") == "make_drink"
        else "serve"   # tutti gli altri casi
    ),
    {
        "list_drinks": "list_drinks",
        "check_inventory": "check_inventory",
        "serve": "serve",
    }
)



# da list_drinks a serve
graph.add_edge("list_drinks", "serve")
# da brew a serve
graph.add_edge("brew", "serve")
graph.add_edge("serve", END) # ultimo

app = graph.compile()


# Version without LLM. LLM used only for interpret_order
# def interactive_loop():
#     memory.init_db()
#     user_id = "anon"  # puoi estendere per utenti reali
#     while True:
#         user_input = input("Che caffè vuoi? (scrivi 'exit' per uscire) > ").strip()
#         if user_input.lower() in ("exit","quit"):
#             break
#         parsed = interpret_order(user_input)
#         if not parsed:
#             # chiedi chiarimenti
#             clar = input("Non ho capito bene. Puoi ripetere più semplicemente? > ")
#             parsed = interpret_order(clar)
#             if not parsed:
#                 print("Mi dispiace, riproviamo più tardi.")
#                 continue

#         # mostra riepilogo e chiedi conferma
#         print("Ho interpretato così:", parsed)
#         ok = input("Confermi? (s/n) > ").strip().lower()
#         if ok not in ("s","si","sì","y","yes"):
#             print("Ok, riprova a descrivere il caffè.")
#             continue

#         if parsed.get("action") == "list_drinks":
#             drinks = get_available_drinks()
#             if drinks:
#                 print("Attualmente posso preparare:\n" + "\n".join(f"- {d} ({q})" for d, q in drinks.items()))
#                 continue
#             else:
#                 print("Mi dispiace, al momento non ho drink disponibili.")
#                 continue
#         elif parsed.get("action") == "make_drink":
#             out = brew_coffee(parsed, user_id=user_id)
#             print(out)

#         else:
#             print("Azione non riconosciuta. Riprova.", parsed)

#         inv_ok, msg = check_inventory(parsed)
#         if not inv_ok:
#             print(msg)
#             continue

#         # attempt decrement
#         if not decrement_inventory_atomic(parsed):
#             print("Sembra che la disponibilità sia cambiata... riprova.")
#             continue

# Verison with full LLM, also for final reply
def interactive_loop2():
    memory.init_db()
    user_id = "anon"
    while True:
            user_input = input("Che caffè vuoi? (scrivi 'exit' per uscire) > ").strip()
            if user_input.lower() in ("exit", "quit"):
                break

            # Start the graph with user input
            state = app.invoke({"order": user_input, "user_id": user_id})

            # The graph updates state through nodes

            msg = state.get("message", "Errore: nessuna risposta generata.")
            print(msg)

if __name__ == "__main__":
    interactive_loop2()
