def get_consumption_history(service): return service.history()
def get_latest_consumption(service):
    history=service.history()
    return history[-1] if history else None
