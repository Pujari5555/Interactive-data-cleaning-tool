from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('contact/', views.contact_details, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cleaning/', views.cleaning_view, name='cleaning'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('validate_file/', views.validate_file, name='validate_file'),
    path('check_missing_values/', views.check_missing_values, name='check_missing_values'),
    path('handle_missing_values/', views.handle_missing_values, name='handle_missing_values'),  # For handling missing values
    path('settings/', views.settings_view, name='settings'),
    path('about-us/', views.about_us_view, name='about_us'),
    path('change-password/', views.change_password, name='change_password'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('faq/', views.faq_view, name='faq'),
    path('remove_duplicates/', views.remove_duplicates, name='remove_duplicates'),
   
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)