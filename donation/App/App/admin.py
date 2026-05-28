from django.contrib import admin
from .models import CashDonation, ProductDonation, ContactMessage

# ==============================================================================
# EDUCATIONAL GUIDE FOR BEGINNERS / FRESHERS:
# How Django Admin Registers and Displays Database Models:
# 
# 1. Registration:
#    Using `@admin.register(ModelName)`, we tell Django to show this database table
#    in the admin panel dashboard (/admin/).
# 
# 2. Customization (ModelAdmin):
#    - `list_display`: Controls which columns are shown in the main table list.
#    - `list_filter`: Adds a sidebar to filter records (e.g. by Pending/Completed status).
#    - `search_fields`: Adds a search bar matching against these specific columns.
#    - `fieldsets`: Groups the input fields on the record editing page into clean sections.
# ==============================================================================

# Register CashDonation model in the admin panel
@admin.register(CashDonation)
class CashDonationAdmin(admin.ModelAdmin):
    # Columns shown in the main donation lists page
    list_display = (
        'donor_name', 
        'donor_email', 
        'amount_usd', 
        'amount_inr', 
        'exchange_rate', 
        'campaign', 
        'payment_method', 
        'transaction_reference_id', 
        'status', 
        'created_at'
    )
    
    # Sidebar filters on the right side
    list_filter = ('status', 'campaign', 'payment_method', 'created_at')
    
    # Search bar searches through these fields
    search_fields = ('donor_name', 'donor_email', 'transaction_reference_id')
    
    # These fields cannot be modified inside the admin form
    readonly_fields = ('amount_inr', 'created_at')
    
    # Sections layout inside the detail form view
    fieldsets = (
        ('Donor Information', {
            'fields': ('donor_name', 'donor_email')
        }),
        ('Donation Details', {
            'fields': ('amount_usd', 'exchange_rate', 'amount_inr', 'campaign', 'payment_method', 'transaction_reference_id')
        }),
        ('Administration', {
            'fields': ('status', 'created_at')
        }),
    )

    # Actions dropdown options at the top
    actions = ['mark_as_completed', 'mark_as_failed']

    @admin.action(description="Mark selected donations as Completed (Received)")
    def mark_as_completed(self, request, queryset):
        rows_updated = queryset.update(status='Completed')
        if rows_updated == 1:
            message_bit = "1 donation was"
        else:
            message_bit = f"{rows_updated} donations were"
        self.message_user(request, f"{message_bit} successfully marked as completed.")

    @admin.action(description="Mark selected donations as Failed")
    def mark_as_failed(self, request, queryset):
        rows_updated = queryset.update(status='Failed')
        if rows_updated == 1:
            message_bit = "1 donation was"
        else:
            message_bit = f"{rows_updated} donations were"
        self.message_user(request, f"{message_bit} successfully marked as failed.")

    # Prevent manual additions in admin panel (donations come from the frontend forms)
    def has_add_permission(self, request):
        return False


# Register ProductDonation model in the admin panel
@admin.register(ProductDonation)
class ProductDonationAdmin(admin.ModelAdmin):
    list_display = (
        'donor_name', 
        'donor_phone', 
        'product_category', 
        'product_name', 
        'product_condition', 
        'status', 
        'created_at'
    )
    
    list_filter = ('status', 'product_category', 'product_condition', 'created_at')
    
    search_fields = ('donor_name', 'donor_email', 'donor_phone', 'product_name', 'pickup_address')
    
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Donor Contact Details', {
            'fields': ('donor_name', 'donor_email', 'donor_phone')
        }),
        ('Product Description', {
            'fields': ('product_category', 'product_name', 'product_description', 'product_condition')
        }),
        ('Collection & Pickup Details', {
            'fields': ('pickup_address', 'pickup_time_preference')
        }),
        ('Internal Tracking', {
            'fields': ('status', 'admin_notes', 'created_at')
        }),
    )

    actions = ['set_status_scheduled', 'set_status_collected', 'set_status_completed']

    @admin.action(description="Schedule pickup for selected products")
    def set_status_scheduled(self, request, queryset):
        rows_updated = queryset.update(status='Scheduled')
        self.message_user(request, f"{rows_updated} product requests updated to 'Pickup Scheduled'.")

    @admin.action(description="Mark selected products as Collected")
    def set_status_collected(self, request, queryset):
        rows_updated = queryset.update(status='Collected')
        self.message_user(request, f"{rows_updated} product requests updated to 'Product Collected'.")

    @admin.action(description="Mark selected product requests as Completed (Distributed)")
    def set_status_completed(self, request, queryset):
        rows_updated = queryset.update(status='Completed')
        self.message_user(request, f"{rows_updated} product requests updated to 'Distributed / Completed'.")

    # Prevent manual additions in admin panel (donations come from the frontend forms)
    def has_add_permission(self, request):
        return False


# Register ContactMessage model in the admin panel
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'donor_email', 'donor_phone', 'subject', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('donor_name', 'donor_email', 'message')
    readonly_fields = ('donor_name', 'donor_email', 'donor_phone', 'subject', 'message', 'created_at')
    
    # Hide the "Add" button entirely since the admin only views incoming submissions
    def has_add_permission(self, request):
        return False
