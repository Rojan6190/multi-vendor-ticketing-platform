from django.core.cache import cache

DEFAULT_TTL = 60 * 5  # 5 minutes


def _version_key(prefix):
    return f"cache_version:{prefix}"


def get_version(prefix):
    version = cache.get(_version_key(prefix))
    if version is None:
        version = 1
        cache.set(_version_key(prefix), version, timeout=None)
    return version


def bump_version(prefix):
    """Call after any write that affects `prefix` — invalidates every
    cached key under it instantly, no key enumeration needed."""
    key = _version_key(prefix)
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=None)


def build_cache_key(prefix, **params):
    version = get_version(prefix)
    query = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)
    return f"{prefix}:v{version}:{query}"