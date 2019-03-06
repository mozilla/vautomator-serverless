
class Response:
    def __init__(self, response_dict):
        self.response_dict = response_dict

    def without_security_headers(self):
        return self.response_dict

    def with_security_headers(self):
        security_response_dict = self.response_dict.copy()
        security_response_dict["headers"] = {
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, HEAD",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Max-Age": "86400",
            "Cache-control": "no-store",
            "Pragma": "no-cache",
            "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; script-src 'none'; upgrade-insecure-requests",
            "Referrer-Policy": "no-referrer",
            "Content-Type": "application/json",
            "X-Content-Type-Options": "nosniff",
            "X-Download-Options": "noopen",
            "X-Frame-Options": "DENY",
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-XSS-Protection": "1; mode = block",
            "Strict-Transport-Security": "max-age = 15768000; includeSubDomains"
        }
        return security_response_dict
