from django.urls import path # type: ignore
from . import views
from . import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.myprofile, name='myprofile'),
    path('predict-and-recommend/summary', views.summary, name='summary'),  
    path('reason', views.reason, name='reason'),  
    path('predict-and-recommend/results', views.results, name='results'), 
    path('about/', views.about, name='about'),
    path('churn-rate-and-recommendations', views.churn_rate_and_recommendations, name='churn-rate-and-recommendations'),
    path('lockscreen', views.lockscreen_view, name='lockscreen'),
    path('passwordrecovery', views.passwordrecovery, name='passwordrecovery'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('predict-and-recommend/', views.predict_and_recommend_view, name='predict-and-recommend'),  
    
]

