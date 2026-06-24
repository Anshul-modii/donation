from django.contrib import admin
from django.urls import path
from . import views

# ==============================================================================

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
    path('', views.index_view, name='home'),                      # Public landing page is the home page at http://127.0.0.1:8000/
    path('index/', views.index_view, name='index'),               # Keep /index/ URL pointing to index_view for compatibility
    path('admin-login/', views.login_view, name='admin_login'),   # Admin login page at http://127.0.0.1:8000/admin-login/
    path('about/', views.about_view, name='about'),               # About page (public)
    path('donate/', views.donate_view, name='donate'),            # Donate page (public)
    path('contact/', views.contact_view, name='contact'),         # Contact page (public)
    path('admin-dashboard/', views.admin_home_view, name='admin_home'),  # Admin dashboard (staff only)
    path('logout/', views.logout_view, name='logout'),            # Logout endpoint
    
    # API ENDPOINTS (Receives AJAX form data and processes it behind the scenes)
    path('donate/cash/', views.donate_cash_view, name='donate_cash'),       # Handles cash donation submits
    path('donate/product/', views.donate_product_view, name='donate_product'), # Handles product donation submits
    path('contact/submit/', views.contact_submit_view, name='contact_submit'), # Handles contact messages
    
    # Built-in django admin panel route
    path('admin/', admin.site.urls),                             # Matches http://127.0.0.1:8000/admin/
]
