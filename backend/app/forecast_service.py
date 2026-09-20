from decimal import Decimal
from app.billing_service import calculate_tiers

class ForecastService:
    @staticmethod
    def predict(values,tiers):
        values = [Decimal(v) for v in values[-3:]]
        if len(values)<2: return {'available':False,'reason':'Cần ít nhất 2 kỳ dữ liệu.','source':'FORECAST'}
        weights = list(range(1,len(values)+1))
        predicted = (sum(v*w for v,w in zip(values,weights))/sum(weights)).quantize(Decimal('0.001'))
        amount,_ = calculate_tiers(predicted,tiers)
        return {'available':True,'predicted_consumption':str(predicted),'predicted_amount':str(amount),'confidence':'low' if len(values)<3 else 'medium','method':'weighted_moving_average','period_count':len(values),'source':'FORECAST','label':'Ước tính, không phải hóa đơn chính thức'}
