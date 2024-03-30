from datetime import datetime
from aiohttp import web
from darwin.postprocessing.corrector import Corrector
from darwin.sampling.backend import BackendType
from darwin.sampling.models import ModelType
from darwin.sampling.sampler import Sampler
from darwin.postprocessing.validation import validate_syntax


class Server:
    def __init__(self, host: str, port: int) -> None:
        self.app = web.Application()
        self.app.add_routes([web.get("/", self.index)])

    def start_server(self):
        web.run_app(self.app)

    async def index(self, request: web.Request) -> web.Response:
        return web.Response(text="Unimplemented")


class SamplerServer(Server):
    def __init__(
        self, host: str, port: int, backend: BackendType, model: ModelType, **kwargs
    ) -> None:
        super().__init__(host, port)
        self.app.add_routes([web.post("/sample", self.sample)])
        self.active = False
        self.last_sample_time = -1
        self.n_samples = 0
        self.sampler = Sampler(backend=backend, model=model, **kwargs)

    async def index(self, request: web.Request):
        info = {
            "active?": self.active,
            "last_sample": "never"
            if self.last_sample_time == -1
            else str(self.last_sample_time),
            "n_samples": self.n_samples,
        }
        return web.json_response(data=info)

    async def sample(self, request: web.Request) -> web.Response:
        request = await request.json()
        if "prompt" not in request:
            return web.Response(
                text="Please provide prompt as request body",
                status=400,
                reason="Not enough information",
            )

        self.last_sample_time = datetime.now()
        self.n_samples += 1
        self.active = True
        result = await self.sampler.sample(request["prompt"])
        self.active = False
        return web.Response(text=result)


class PostProcesorServer(Server):
    def __init__(
        self, host: str, port: int, backend: BackendType, model: ModelType, **kwargs
    ) -> None:
        super().__init__(host, port)
        self.app.add_routes([web.post("/verify", self.verify)])
        self.app.add_routes([web.post("/correct", self.correct)])
        self.active = False
        self.last_process_time = -1
        self.n_corrections = 0
        self.n_validations = 0
        self.corrector = Corrector(backend=backend, model_name=model, **kwargs)

    async def index(self, request: web.Request):
        info = {
            "active?": self.active,
            "last_process_time": "never"
            if self.last_process_time == -1
            else str(self.last_process_time),
            "n_corrections": self.n_corrections,
            "n_validations": self.n_validations,
        }
        return web.json_response(data=info)

    async def verify(self, request: web.Request):
        request = await request.json()
        if "code" not in request:
            return web.Response(
                text="Please specify the code to be validated through json with the key `code`"
            )
        self.n_validations += 1
        self.last_process_time = datetime.now()
        if validate_syntax(request["code"]):
            return web.Response(text=request["code"])
        return web.Response(text="False")

    async def correct(self, request: web.Request):
        if self.corrector:
            self.n_corrections += 1
            self.last_process_time = datetime.now()
            request = await request.json()
            result = await self.corrector.fix(request["code"])
            return web.Response(text=result)

        return web.Response(
            text="Reached API /correct but server was never instantiated with a corrector"
        )
