from app import create_app 
from app.admin.services import get_dashboard_stats 
app=create_app('development') 
with app.app_context(): 
    s=get_dashboard_stats() 
    print('weekly_series', s['weekly_revenue_series']) 
    print('weekly_top_last', s['weekly_top_products'][-1] if s['weekly_top_products'] else None) 
    print('monthly_series', s['monthly_revenue_series']) 
    print('monthly_top_last', s['monthly_top_products'][-1] if s['monthly_top_products'] else None) 
