from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('', views.Top.as_view(), name='top'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<uidb64>/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),

    path('person_list/', views.PersonList.person_list, name='person_list'),
    path('person_list/add/', views.PersonList.person_edit, name='person_add'),
    path('person_list/mod/<int:person_id>/', views.PersonList.person_edit, name='person_mod'),
    path('person_list/del/<int:person_id>/', views.PersonList.person_del, name='person_del'),

    path('cost_list/<int:person_id>/', views.CostList.cost_list, name='cost_list'),
    path('cost_list/add/<int:person_id>/', views.CostList.cost_edit, name='cost_add'),
    path('cost_list/mod/<int:person_id>/<int:cost_id>/', views.CostList.cost_edit, name='cost_mod'),
    path('cost_list/del/<int:person_id>/<int:cost_id>/', views.CostList.cost_del, name='cost_del'),
]
