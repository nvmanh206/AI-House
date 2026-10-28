def get_bill_history(service, *args, **kwargs): return service.bills()
def get_current_bill(service, *args, **kwargs):
    bills=service.bills()
    return bills[0] if bills else None
