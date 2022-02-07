from pygizmo.containers.data_model import DataModel

Query: ParamType = ParamType("Query")
Path: ParamType = ParamType("Path")
Body: ParamType = ParamType("Body")
Header: ParamType = ParamType("Header")


class Endpoint(DataModel):
    def setup(self):
        pass

    def callback(self, response: httpx.Response):
        if self.RequestConfig.return_full_response:
            return response
        try:
            self.response_to_output_model(response)
        except JSONDecodeError:
            return response.content

    def response_to_output_model(self, response: httpx.Response):
        if self.RequestConfig.output_model:
            output_data = response.json()
            if self.RequestConfig.output_key:
                output_data = output_data.get(self.RequestConfig.output_key)
            if output_data:
                return parse_obj_as(self.RequestConfig.output_model, output_data, from_trusted_source=True)  # type: ignore[arg-type]
            return output_data

    class RequestConfig:
        output_model: DataModel = None
        output_key = None
        exclude_none_params = True
        exclude_none_body = False
        format_url = True
        raise_for_status = False
        return_full_response = False

        method: str
        url: URLTypes = ""
        content: RequestContent = None
        data: RequestData = None
        files: RequestFiles = None
        body: Any = None
        params: QueryParamTypes = None
        headers: HeaderTypes = None
        cookies: CookieTypes = None
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT
        extensions: dict = None

    class ResponseModel:
        pass

    @property
    def params(self):
        return self._filter_values("Query", self.RequestConfig.exclude_none_params)

    @property
    def body(self):
        return self._filter_values("Body", self.RequestConfig.exclude_none_body)

    @property
    def headers(self):
        return self._filter_values("Header", True)

    @property
    def url(self):
        if self.RequestConfig.format_url is True and self.RequestConfig.url:
            values = self._filter_values("Path", False)
            return self.RequestConfig.url.format(**values)
        return self.RequestConfig.url

    def _filter_values(self, param_type: str, exclude_nones: bool):
        values = self.dict(json_format=True)
        items = {
            k: values.get(k)
            for k, v in self.__fields__.items()
            if v.field_info.extra.get("param_type", "Query") == param_type
        }
        if exclude_nones and items:
            items = {k: v for k, v in items.items() if v is not None}
        return items

    def _get_request_key(self, key: str):
        try:
            return getattr(self, key)
        except AttributeError:
            return getattr(self.RequestConfig, key, ...)

    @property
    def request_data(self):
        keys = [
            "method",
            "url",
            "content",
            "data",
            "files",
            "params",
            "headers",
            "cookies",
            "auth",
            "follow_redirects",
            "timeout",
            "extensions",
        ]
        data = {k: self._get_request_key(k) for k in keys}
        data["json"] = self._get_request_key("body")
        return data

    @classmethod
    def _get_request_config(cls):
        self_config = getattr(cls, "RequestConfig", None)
        base_classes = []
        if self_config and self_config != Endpoint.RequestConfig:
            base_classes.append(self_config)
        return type("RequestConfig", tuple(base_classes), {})

    def __new__(cls, *args, **kwargs):
        config = cls._get_request_config()

        cls.RequestConfig: Type[Endpoint.RequestConfig] = inherit_config(  # type: ignore
            config, Endpoint.RequestConfig  # type: ignore
        )
        return super().__new__(cls, *args, **kwargs)
