def get_bill_history(service): return service.bills()
def get_current_bill(service):
    bills=service.bills()
    return bills[0] if bills else None
