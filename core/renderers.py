from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    """
    Last line of defense: wraps ANY payload that reaches DRF's renderer
    in {status, message, data} — even responses that never passed through
    custom_exception_handler or APIResponse.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200

        # Already wrapped (by APIResponse or custom_exception_handler)
        if isinstance(data, dict) and "status" in data and "data" in data:
            return super().render(data, accepted_media_type, renderer_context)

        if status_code >= 400:
            wrapped = {
                "status": "error",
                "message": data if not isinstance(data, dict) else data.get("detail", "Error"),
                "data": None,
            }
        else:
            wrapped = {"status": "success", "message": "Success", "data": data}

        return super().render(wrapped, accepted_media_type, renderer_context)
    