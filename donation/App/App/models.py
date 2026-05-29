from django.db import models

# ==============================================================================

# How Django Models Connect to the Database and the Frontend:
# 
# 1. Models (Database Schema):
#    This file (models.py) defines the structure of our tables in the SQLite database.
#    Each class is a Table, and each variable is a Column (Field).
# 
# 2. Migration:
#    When we run "python manage.py makemigrations", Django reads this file and creates
#    instructions (migrations) to build these tables in SQL.
#    When we run "python manage.py migrate", Django actually builds or updates those tables.
# 
# 3. Connectivity to Frontend:
#    When a user submits a form on the frontend, Javascript sends the data as a POST request.
#    A Django View (views.py) receives that data and calls the model, like:
#    `CashDonation.objects.create(donor_name=..., ...)` to insert a row in the database.
# ==============================================================================

class CashDonation(models.Model):
    """
    Model (Table) to store cash/amount donations.
    
    HOW FRONTEND FIELDS MAP TO THIS MODEL:
    - HTML input field value -> backend views.py -> saves to database fields below.
    - 'donor_name'     <-- maps to frontend input id='donorName'
    - 'donor_email'    <-- maps to frontend input id='donorEmail'
    - 'amount_inr'     <-- maps to donationAmount variable
    - 'campaign'       <-- maps to dropdown id='campaignSelect'
    - 'payment_method' <-- maps to checked radio input name='paymentMethod' (card, paypal, upi)
    - 'transaction_reference_id' <-- maps to input id='upiRefNumber' (only for UPI transfers)
    """
    
    CAMPAIGN_CHOICES = [
        ('general', 'General Needs (Where it is needed most)'),
        ('water', 'Clean Drinking Water Wells'),
        ('education', 'Books & Classrooms Fund'),
        ('medical', 'Mobile Health Clinics'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('upi', 'UPI Payment'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Completed', 'Completed (Received)'),
        ('Failed', 'Failed'),
    ]

    # CharField means a short text field (e.g. name, title)
    donor_name = models.CharField(max_length=255, verbose_name="Donor Full Name")
    
    # EmailField automatically validates that the text is a valid email address format
    donor_email = models.EmailField(verbose_name="Donor Email Address")
    
    # DecimalField is ideal for money/currency fields to avoid rounding errors
    amount_inr = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount in Rupees (₹)")
    
    # Keeping old USD fields optional so database compatibility is maintained
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Amount in USD ($)")
    exchange_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="USD to INR Exchange Rate")
    
    # Choices fields restrict the input to the defined lists above
    campaign = models.CharField(max_length=50, choices=CAMPAIGN_CHOICES, default='general', verbose_name="Direct Donation To")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card', verbose_name="Payment Method")
    
    # UPI transaction Reference ID (e.g. 12-digit number)
    transaction_reference_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Transaction Reference ID", help_text="For UPI Reference ID or card transaction ID")
    
    # Donation Status allows the admin/charity owner to track payment verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed', verbose_name="Donation Status")
    
    # DateTimeField with auto_now_add=True saves the date and time automatically when the record is created
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Donation Date")

    def __str__(self):
        return f"{self.donor_name} - ₹{self.amount_inr}"

    class Meta:
        verbose_name = "Cash Donation"
        verbose_name_plural = "Cash Donations"
        ordering = ['-created_at']


class ProductDonation(models.Model):
    """
    Model (Table) to store physical product donation requests (books, clothes, furniture, etc.).
    
    HOW FRONTEND FIELDS MAP TO THIS MODEL:
    - 'donor_name'             <-- maps to input id='prodDonorName'
    - 'donor_email'            <-- maps to input id='prodDonorEmail'
    - 'donor_phone'            <-- maps to input id='prodDonorPhone'
    - 'product_category'       <-- maps to dropdown id='prodCategory' (book, food, etc.)
    - 'product_name'           <-- maps to input id='prodName'
    - 'product_description'    <-- maps to textarea id='prodDesc'
    - 'product_condition'      <-- maps to dropdown id='prodCondition'
    - 'pickup_address'         <-- maps to textarea id='prodAddress'
    - 'pickup_time_preference' <-- maps to input id='prodPickupTime'
    """
    CATEGORY_CHOICES = [
        ('book', 'Books & Stationery'),
        ('food', 'Food & Groceries'),
        ('clothes', 'Clothes & Apparel'),
        ('furniture', 'Furniture & Household'),
        ('machine', 'Machines & Electronic Appliances'),
        ('other', 'Other Products'),
    ]
    
    CONDITION_CHOICES = [
        ('New', 'Brand New / Sealed'),
        ('Like New', 'Like New / Barely Used'),
        ('Good', 'Good / Fully Functional'),
        ('Fair', 'Fair / Needs minor cleanup'),
        ('Poor', 'Poor / Needs repair'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Scheduled', 'Pickup Scheduled'),
        ('Collected', 'Product Collected'),
        ('Completed', 'Distributed / Completed'),
        ('Cancelled', 'Cancelled / Declined'),
    ]

    donor_name = models.CharField(max_length=255, verbose_name="Donor Name")
    donor_email = models.EmailField(verbose_name="Donor Email")
    donor_phone = models.CharField(max_length=20, verbose_name="Donor Contact Number")
    
    product_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Product Category")
    product_name = models.CharField(max_length=255, verbose_name="Product Name / Title", help_text="e.g. 'Science textbooks', 'Winter jackets'")
    product_description = models.TextField(blank=True, verbose_name="Product Description & Quantity", help_text="List details, quantities, and condition notes")
    product_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='Good', verbose_name="Condition")
    
    pickup_address = models.TextField(verbose_name="Collection / Pickup Address")
    pickup_time_preference = models.CharField(max_length=255, blank=True, verbose_name="Preferred Pickup Day/Time", help_text="e.g. 'Weekends morning', 'Any weekday after 5 PM'")
    
    # Internal status tracking for charity owner logistics
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Pickup / Distribution Status")
    admin_notes = models.TextField(blank=True, verbose_name="Admin Notes", help_text="Internal notes for scheduling, driver names, or distribution logs")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Request Date")

    def __str__(self):
        return f"{self.donor_name} - {self.get_product_category_display()} ({self.product_name})"

    class Meta:
        verbose_name = "Product Donation Request"
        verbose_name_plural = "Product Donation Requests"
        ordering = ['-created_at']


class ContactMessage(models.Model):
    """
    Model (Table) to store contact/inquiry messages submitted by visitors.
    
    HOW FRONTEND FIELDS MAP TO THIS MODEL:
    - 'donor_name'    <-- maps to input id='contactName'
    - 'donor_email'   <-- maps to input id='contactEmail'
    - 'donor_phone'   <-- maps to input id='contactPhone'
    - 'subject'       <-- maps to dropdown id='contactSubject'
    - 'message'       <-- maps to textarea id='contactMessage'
    """
    SUBJECT_CHOICES = [
        ('donation', 'Donation & Tax Invoice Help'),
        ('volunteer', 'Volunteering Opportunities'),
        ('partnership', 'Corporate Partnerships'),
        ('media', 'Media & PR Inquiries'),
        ('other', 'General Questions'),
    ]

    donor_name = models.CharField(max_length=255, verbose_name="Sender Name")
    donor_email = models.EmailField(verbose_name="Sender Email")
    donor_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Sender Phone (Optional)")
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, default='other', verbose_name="Subject of Inquiry")
    message = models.TextField(verbose_name="Message Content")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Received Date")

    def __str__(self):
        return f"{self.donor_name} - {self.get_subject_display()}"

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']