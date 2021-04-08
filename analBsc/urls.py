from django.urls import path
from . import views, legacy, class_views

urlpatterns = [
    path('', views.index_html),
    path('html', legacy.index),
    path('addresses/', class_views.AddressInfoView.as_view()),
    path('update/', views.updateCache),
    path('stackmergest/', views.stack_merge_graphs_Stacking_View),
    path('stackmergelp/', views.stack_merge_graphs_Farming_View),
    path('totalsupply/', views.total_supply_View),
    path('buysold/', views.check_hash),
    path('yesterday/', views.yesterday_delta),
    path('profile/', class_views.ProfileListView.as_view()),
    path('profile/<int:pk>', class_views.ProfileDetailView.as_view()),
    path('transactions/<int:pk>', views.profile_dfx_transactions),
    path('admininfo/', views.admin_info),
    path('changetgname/', views.change_tg_user_name)
]
