import json
import urllib.request
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .models import CashDonation, ProductDonation, ContactMessage

# ==============================================================================
# EDUCATIONAL GUIDE FOR BEGINNERS / FRESHERS:
# How Django Views (Controllers) handle Client Requests:
# 
# 1. Routing:
#    When a user visits a URL (e.g. /donate/), Django matches it in urls.py and
#    runs the corresponding view function here.
# 
# 2. View Functions:
#    - Page views (like index_view, donate_view) render HTML templates.
#    - API views (like donate_cash_view) handle form submissions (AJAX POST),
#      perform validations, create/save database rows, and return JSON responses.
# ==============================================================================


# ==========================================
# CURRENCY CONVERSION UTILITY
# ==========================================
def get_usd_to_inr_rate():
    """
    Attempts to fetch the live USD to INR exchange rate from a public API.
    If the API call fails (network issue, timeout, etc.), it returns a fallback rate.
    """
    fallback_rate = 83.50  # Stable fallback rate
    url = "https://open.er-api.com/v6/latest/USD"
    
    try:
        # Fetching JSON from exchange rate API (timeout in 3 seconds)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            rates = data.get("rates", {})
            inr_rate = rates.get("INR")
            if inr_rate:
                return float(inr_rate)
    except Exception as e:
        # If API fails, print error and use the fallback rate
        print(f"Failed to fetch live exchange rate: {e}. Using fallback rate: {fallback_rate}")
    
    return fallback_rate


# ==========================================
# PAGE ROUTING VIEWS
# ==========================================
def index_view(request):
    """Renders the index/home page (index.html)."""
    return render(request, 'index.html')

def about_view(request):
    """Renders the about us page (about.html)."""
    return render(request, 'about.html')

def donate_view(request):
    """
    Renders the interactive donation portal page (donate.html).
    Passes the current exchange rate to the page so it can display the conversion live.
    """
    exchange_rate = get_usd_to_inr_rate()
    context = {
        'exchange_rate': exchange_rate
    }
    return render(request, 'donate.html', context)

def contact_view(request):
    """Renders the contact us page (contact.html)."""
    return render(request, 'contact.html')

def login_view(request):
    """Renders the dashboard portal login page (login.html)."""
    return render(request, 'login.html')


# ==========================================
# BACKEND API ENDPOINTS
# ==========================================

@require_POST
def donate_cash_view(request):
    """
    Handles Cash/Amount donation form submissions.
    Expects standard POST data or JSON data from front-end AJAX.
    Processes donation directly in Rupees (INR).
    
    FRESHER-FRIENDLY CONNECTIVITY FLOW:
    1. Client (Javascript in donate.html) makes a POST fetch request to '/donate/cash/'.
    2. View retrieves values from the POST payload (donor_name, donor_email, amount_inr, etc.).
    3. View validates inputs (ensuring non-empty, and minimum of ₹200.00).
    4. View determines payment status (UPI defaults to 'Pending' review; Card/Paypal defaults to 'Completed').
    5. View inserts/saves record using Django ORM: `CashDonation.objects.create(...)`.
    6. View sends back a success JSON response `{'status': 'success', ...}`.
    """
    # Parse data from standard form-encoded POST or JSON payload
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'error': 'Invalid JSON format'}, status=400)
    else:
        data = request.POST

    # Retrieve values
    donor_name = data.get('donor_name')
    donor_email = data.get('donor_email')
    amount_inr_raw = data.get('amount_inr')
    campaign = data.get('campaign', 'general')
    payment_method = data.get('payment_method', 'card')
    transaction_reference_id = data.get('transaction_reference_id')

    # Basic validations
    if not all([donor_name, donor_email, amount_inr_raw]):
        return JsonResponse({'status': 'error', 'error': 'Required fields (Name, Email, Amount) are missing'}, status=400)
    
    try:
        amount_inr = float(amount_inr_raw)
        if amount_inr < 200.00:
            return JsonResponse({'status': 'error', 'error': 'Minimum donation amount is ₹200.00 INR'}, status=400)
    except ValueError:
        return JsonResponse({'status': 'error', 'error': 'Invalid donation amount value'}, status=400)

    # Create & Save record directly in INR
    try:
        # Default status for UPI is Pending validation of transaction reference ID.
        # For Card and Paypal we can set to Completed for this demo.
        donation_status = 'Pending' if payment_method == 'upi' else 'Completed'

        donation = CashDonation.objects.create(
            donor_name=donor_name,
            donor_email=donor_email,
            amount_inr=amount_inr,
            amount_usd=None,
            exchange_rate=None,
            campaign=campaign,
            payment_method=payment_method,
            transaction_reference_id=transaction_reference_id,
            status=donation_status
        )
        
        # Return summary response to frontend Javascript callback
        return JsonResponse({
            'status': 'success',
            'donation_id': donation.id,
            'amount_inr': round(float(donation.amount_inr), 2),
            'campaign': donation.campaign,
            'donor_name': donation.donor_name
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': f'Failed to process donation: {str(e)}'}, status=500)


@require_POST
def donate_product_view(request):
    """
    Handles Product donation form requests.
    Saves product details and pickup location address to the database.
    
    FRESHER-FRIENDLY CONNECTIVITY FLOW:
    1. Client (Javascript in donate.html) submits the product donation form.
    2. View retrieves product details (category, title, condition, pickup address, phone).
    3. View saves record to ProductDonation table with 'Pending Review' status.
    4. View returns status response. Charity admin can schedule pickup inside Django Admin panel.
    """
    # Parse data from standard form-encoded POST or JSON payload
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'error': 'Invalid JSON format'}, status=400)
    else:
        data = request.POST

    # Retrieve values
    donor_name = data.get('donor_name')
    donor_email = data.get('donor_email')
    donor_phone = data.get('donor_phone')
    product_category = data.get('product_category', 'other')
    product_name = data.get('product_name')
    product_description = data.get('product_description', '')
    product_condition = data.get('product_condition', 'Good')
    pickup_address = data.get('pickup_address')
    pickup_time_preference = data.get('pickup_time_preference', '')

    # Validations
    if not all([donor_name, donor_email, donor_phone, product_name, pickup_address]):
        return JsonResponse({'status': 'error', 'error': 'Required fields (Name, Email, Phone, Product Name, and Pickup Address) are missing'}, status=400)

    # Save details
    try:
        pickup_request = ProductDonation.objects.create(
            donor_name=donor_name,
            donor_email=donor_email,
            donor_phone=donor_phone,
            product_category=product_category,
            product_name=product_name,
            product_description=product_description,
            product_condition=product_condition,
            pickup_address=pickup_address,
            pickup_time_preference=pickup_time_preference,
            status='Pending'  # Wait for admin overview to schedule or collect
        )
        
        return JsonResponse({
            'status': 'success',
            'request_id': pickup_request.id,
            'donor_name': pickup_request.donor_name,
            'product_name': pickup_request.product_name,
            'product_category': pickup_request.get_product_category_display(),
            'status_label': pickup_request.get_status_display()
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': f'Failed to process product donation request: {str(e)}'}, status=500)


@require_POST
def contact_submit_view(request):
    """
    Handles Contact/Inquiry form submissions.
    Saves message details from the contact page to the database.
    
    FRESHER-FRIENDLY CONNECTIVITY FLOW:
    1. Client (Javascript in contact.html) sends a POST fetch request to '/contact/submit/'.
    2. View retrieves fields (donor_name, donor_email, donor_phone, subject, message).
    3. View validates that name, email, and message are not empty.
    4. View inserts/saves record using Django ORM: `ContactMessage.objects.create(...)`.
    5. View sends back success JSON response.
    """
    # Parse data from standard form-encoded POST or JSON payload
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'error': 'Invalid JSON format'}, status=400)
    else:
        data = request.POST

    # Retrieve values
    donor_name = data.get('donor_name')
    donor_email = data.get('donor_email')
    donor_phone = data.get('donor_phone', '')
    subject = data.get('subject', 'other')
    message = data.get('message')

    # Basic validations
    if not all([donor_name, donor_email, message]):
        return JsonResponse({'status': 'error', 'error': 'Required fields (Name, Email, and Message) are missing'}, status=400)

    # Save to database
    try:
        msg = ContactMessage.objects.create(
            donor_name=donor_name,
            donor_email=donor_email,
            donor_phone=donor_phone,
            subject=subject,
            message=message
        )
        return JsonResponse({
            'status': 'success',
            'message_id': msg.id,
            'donor_name': msg.donor_name
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': f'Failed to save contact message: {str(e)}'}, status=500)

