from typing import Any, Callable, Dict, Union

from functools import partial

import httpx
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from httpx._types import (
    AuthTypes,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
)

from pygizmo.containers.data_model import DataModel


class SyncClient(httpx.Client):
    def __init__(self, output_model: DataModel = None, response_methods: Dict[str, Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self.output_model = output_model
        self.response_methods = response_methods or {}

    def request(
        self,
        method: str,
        url: URLTypes,
        *,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json: Any = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None,
        to_output_model: Callable = None,
    ) -> httpx.Response:
        request_data = dict(
            method=method,
            url=url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )
        response = super().request(**request_data)
        setattr(response, "request_data", request_data)
        if to_output_model:
            setattr(
                response,
                "to_output_model",
                partial(to_output_model, response=response),
            )
        for name, func in self.response_methods.items():
            setattr(response, name, partial(func, response=response))

        if self.output_model:
            response_json = response.json()
            if isinstance(response_json, list):
                model_data = list(self.output_model.from_trusted_source(record) for record in response_json)
            else:
                model_data = self.output_model.from_trusted_source(response_json)
            setattr(response, "model", model_data)
        return response
