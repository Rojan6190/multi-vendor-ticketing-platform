from django.db import models

class UserRole(models.TextChoices): 
    ADMIN = "admin", "Admin"
    ORGANIZER = "organizer", "Organizer"
    ATTENDEE = "attendee", "Attendee" 

class BookingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED = "expired", "Expired"

class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    FAILED = "failed", "Failed"
    SUCCESS = "success", "Success"
    REFUNDED = "refunded", "Refunded"

class EventStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"

#vendor related enums
class VendorStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"

class DocumentType(models.TextChoices):
    BUSINESS_REGISTRATION = "business_registration", "Business Registration"
    ID_PROOF = "id_proof", "ID Proof"

class PayoutMethod(models.TextChoices):
    BANK = "bank", "Bank Account"
    WALLET = "wallet", "Mobile Wallet"