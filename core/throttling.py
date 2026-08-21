from rest_framework.throttling import SimpleRateThrottle

class BurstRateThrottle(SimpleRateThrottle):
    # Tight limit for sensitive endpoints (login, payment, OTP).
    
    scope = "burst"

    def get_cache_key(self, request, view): #need to use Redis for production
        ident = request.user.pk if request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

class SustainedRateThrottle(SimpleRateThrottle):
    # Looser, longer-window limit for general API abuse prevention

    scope = "sustained"

    def get_cache_key(self, request, view):
        ident = request.user.pk if request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

class OTPThrottle(SimpleRateThrottle):
    #Tight per-user limit so nobody can spam OTP requests or brute-force a code.
    scope = "otp"

    def get_cache_key(self, request, view):
        ident = request.user.pk if request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}