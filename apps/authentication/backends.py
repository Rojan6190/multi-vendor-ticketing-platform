"""
Not needed yet: password login already works via Django's default ModelBackend
(CustomUser.USERNAME_FIELD = "email"), and Google OAuth issues JWTs directly in
views.py without touching the backend chain. Kept as a stub for future backends
(e.g. API-key auth for third-party integrators).
"""