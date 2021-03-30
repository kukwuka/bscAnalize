from django.urls import path
from . import views
from . import legacy

urlpatterns = [
    path('', views.index_html),
    path('html', legacy.index),
    path('home/', views.AddressInfoView.as_view()),
    path('update/', views.updateCache),
    path('buysolddfx/', views.buy_sold_graphs_DFX_View),
    path('buysoldbusd/', views.buy_sold_graphs_BUSD_View),
    path('stackmergest/', views.stack_merge_graphs_Stacking_View),
    path('stackmergelp/', views.stack_merge_graphs_Farming_View),
    path('totalsupply/', views.total_supply_View),
]

