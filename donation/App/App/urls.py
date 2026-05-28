from django.contrib import admin
from django.urls import path
from . import views

# ==============================================================================
# EDUCATIONAL GUIDE FOR BEGINNERS / FRESHERS:
# How Django Routing (URLs) Connects Client Requests to Views:
# 
# 1. urlpatterns List:
#    This list maps web browser URLs (like '/contact/' or '/donate/cash/') to 
#    specific views (functions in views.py).
# 
# 2. Path Arguments:
#    - Argument 1: The URL string matches what the user enters in the browser.
#    - Argument 2: The View function (e.g. `views.contact_view`) that will run.
#    - Argument 3: The `name` parameter allows us to link pages in HTML easily
#      using template tags like `{% url 'home' %}` without hardcoding URLs.
# ==============================================================================

urlpatterns = [
    # PAGE ROUTING (Renders HTML templates to the user)
    path('', views.index_view, name='home'),                      # Matches http://127.0.0.1:8000/
    path('about/', views.about_view, name='about'),               # Matches http://127.0.0.1:8000/about/
    path('donate/', views.donate_view, name='donate'),            # Matches http://127.0.0.1:8000/donate/
    path('contact/', views.contact_view, name='contact'),         # Matches http://127.0.0.1:8000/contact/
    path('login/', views.login_view, name='login'),               # Matches http://127.0.0.1:8000/login/
    
    # API ENDPOINTS (Receives AJAX form data and processes it behind the scenes)
    path('donate/cash/', views.donate_cash_view, name='donate_cash'),       # Handles cash donation submits
    path('donate/product/', views.donate_product_view, name='donate_product'), # Handles product donation submits
    path('contact/submit/', views.contact_submit_view, name='contact_submit'), # Handles contact messages
    
    # Built-in django admin panel route
    path('admin/', admin.site.urls),                             # Matches http://127.0.0.1:8000/admin/
]
