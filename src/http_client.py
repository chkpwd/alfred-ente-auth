import ssl
from functools import lru_cache

import requests
import truststore


class SystemTrustAdapter(requests.adapters.HTTPAdapter):
    """
    Verify HTTPS certificates with the macOS trust store instead of the bundled CA list.

    An explicitly configured CA bundle (`verify=<path>` or REQUESTS_CA_BUNDLE) is left as is.
    """

    def __init__(self):
        self.ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        super().__init__()

    def build_connection_pool_key_attributes(self, request, verify, cert=None):
        host_params, pool_kwargs = super().build_connection_pool_key_attributes(
            request, verify, cert
        )
        if verify is True:
            pool_kwargs["ssl_context"] = self.ssl_context
        return host_params, pool_kwargs

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        if proxy.lower().startswith("https://"):
            proxy_kwargs.setdefault("proxy_ssl_context", self.ssl_context)
        return super().proxy_manager_for(proxy, **proxy_kwargs)


@lru_cache(maxsize=1)
def get_icon_session() -> requests.Session:
    session = requests.Session()
    session.mount("https://", SystemTrustAdapter())
    return session
