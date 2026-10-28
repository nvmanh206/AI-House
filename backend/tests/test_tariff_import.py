import pytest
from app.tariff_import import residential_tiers
from app.billing_service import calculate_tiers
from types import SimpleNamespace

def source(last='11 trở lên'):
    return ('''<main><script>const residentialTableHeaders=["Nhóm", "Cũ", "Mới đồng/kWh quyết định thử"];
    const residentialElectricityData=[{group:"Giá bán lẻ điện sinh hoạt",values:[
    {desc:"Bậc 1: Cho kWh từ 0 - 10",oldPrice:111,newPrice:123},
    {desc:"Bậc 2: Cho kWh từ LAST",oldPrice:222,newPrice:456}]}];</script></main>'''.replace('LAST',last)).encode()

def test_catalog_uses_source_new_prices_and_continuous_limits():
    rows,heading=residential_tiers(source())
    assert rows==[{'from_value':'0','to_value':'10','unit_price':'123'},{'from_value':'10','to_value':None,'unit_price':'456'}]
    assert 'quyết định thử' in heading
    assert calculate_tiers('12',[SimpleNamespace(**r) for r in rows])[0]==2142

def test_incomplete_or_gapped_catalog_is_rejected():
    for text in ('12 trở lên','11 - 20'):
        with pytest.raises(ValueError):residential_tiers(source(text))
