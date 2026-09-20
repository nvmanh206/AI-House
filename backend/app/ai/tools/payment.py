def get_payment_status(service):
    return [{'id':b['id'],'period':b['period'],'status':b['status'],'final_amount':b['final_amount'],'due_date':b['due_date']} for b in service.bills()]
