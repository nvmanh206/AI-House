from decimal import Decimal

class AnomalyService:
    @staticmethod
    def detect(current,history):
        values = [Decimal(v) for v in history[-3:]]
        if len(values)<2: return {'is_anomaly':False,'available':False,'reason':'Cần ít nhất 2 kỳ trước.'}
        baseline = sum(values)/len(values)
        deviation = ((Decimal(current)-baseline)/baseline*100) if baseline else None
        anomalous = deviation is not None and deviation>30
        return {'available':True,'is_anomaly':anomalous,'severity':'medium' if anomalous else 'normal','baseline':str(baseline.quantize(Decimal('.001'))),'current':str(current),'deviation_percent':str(deviation.quantize(Decimal('.01'))) if deviation is not None else None}
