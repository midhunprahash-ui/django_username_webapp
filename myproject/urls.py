from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('accounts/login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),

    
    path('', RedirectView.as_view(pattern_name='unauthorized_employees', permanent=False)),
    
    path('', include('myapp.urls')),
]
