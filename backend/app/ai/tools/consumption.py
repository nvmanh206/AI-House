def get_consumption_history(service, *args, **kwargs): return service.history()
def get_latest_consumption(service, *args, **kwargs):
    history=service.history()
    return history[-1] if history else None
