from typing import Any, Callable, Dict, List, Mapping, Optional, Type, Union

from functools import partial
from json import JSONDecodeError

import httpx
from httpx import BaseTransport, Limits
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from httpx._config import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG
from httpx._types import (
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxiesTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
)
from pydantic import parse_obj_as
from pydantic.config import inherit_config
from pydantic.fields import FieldInfo, Undefined
from pydantic.typing import NoArgAnyCallable

from pygizmo.api_client.clients.sync_client import SyncClient
from pygizmo.containers.data_model import DataModel


class ApiClient:
    url: URLTypes = ""
    output_model: DataModel = None

    auth: AuthTypes = None
    params: Union[DataModel, QueryParamTypes] = None
    headers: HeaderTypes = None
    cookies: CookieTypes = None
    verify: VerifyTypes = True
    cert: CertTypes = None
    http1: bool = True
    http2: bool = False
    proxies: ProxiesTypes = None
    mounts: Mapping[str, BaseTransport] = None
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG
    follow_redirects: bool = False
    limits: Limits = DEFAULT_LIMITS
    max_redirects: int = DEFAULT_MAX_REDIRECTS
    event_hooks: Mapping[str, List[Callable]] = None
    base_url: URLTypes = ""
    transport: BaseTransport = None
    app: Callable = None
    trust_env: bool = True

    def __init__(self):
        self._response_methods = {}

    @property
    def client(self):
        params = self.params.dict() if getattr(self.params, "dict", None) else self.params
        client = SyncClient(
            auth=self.auth,
            params=params,
            headers=self.headers,
            cookies=self.cookies,
            verify=self.verify,
            cert=self.cert,
            http1=self.http1,
            http2=self.http2,
            proxies=self.proxies,
            mounts=self.mounts,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            limits=self.limits,
            max_redirects=self.max_redirects,
            event_hooks=self.event_hooks,
            base_url=self.base_url,
            transport=self.transport,
            app=self.app,
            trust_env=self.trust_env,
            output_model=self.output_model,
            response_methods=self._response_methods,
        )
        if self.url:
            client.base_url = client._merge_url(self.url)
        return client

    @staticmethod
    def paginate(response: httpx.Response) -> httpx.Response:
        return response

    def set_endpoint(self, endpoint):
        def call_endpoint(**kwargs):
            request = endpoint(**kwargs)
            request.setup()

            response = self.client.request(**request.request_data, to_output_model=request.response_to_output_model)

            return request.callback(response)

        return call_endpoint

    def set_response_method(self, name: str, func: Callable):
        self._response_methods.update({name: func})
