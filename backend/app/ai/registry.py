from app.ai.instructions import instructions
from app.ai.tools.household import get_household_profile
from app.ai.tools.consumption import get_consumption_history,get_latest_consumption
from app.ai.tools.billing import get_bill_history,get_current_bill
from app.ai.tools.tariff import get_tariff
from app.ai.tools.payment import get_payment_status
from app.ai.tools.notification import get_upcoming_notifications
from app.ai.tools.knowledge import get_public_tariff

TOOLS={f.__name__:f for f in (get_household_profile,get_consumption_history,get_latest_consumption,get_bill_history,get_current_bill,get_tariff,get_payment_status,get_upcoming_notifications)}
TOOLS['get_public_tariff']=get_public_tariff
SKILLS={
 'public_tariff':['get_public_tariff'],
 'general_chat':[],
 'basic_knowledge':[],
 'configured_tariff':['get_tariff'],
 'household_overview':['get_household_profile','get_consumption_history','get_bill_history'],
 'consumption_analysis':['get_consumption_history'],
 'consumption_comparison':['get_consumption_history','get_bill_history'],
 'bill_analysis':['get_bill_history','get_consumption_history'],
 'bill_forecast':['get_consumption_history','get_tariff'],
 'anomaly_detection':['get_consumption_history'],
 'saving_recommendation':['get_consumption_history'],
 'payment_assistant':['get_payment_status','get_upcoming_notifications'],
 'explain_result':['get_bill_history','get_consumption_history'],
}
