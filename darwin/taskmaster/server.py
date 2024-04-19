import re
from datetime import datetime
from aiohttp import web
from darwin.configuration import EvolverConfig
from darwin.evolving.evolver import Evolver
from darwin.evolving.samples import Sample
from darwin.postprocessing.corrector import Corrector
from darwin.evaluating.evaluator import Evaluator
from darwin.sampling.backend import BackendType
from darwin.sampling.models import ModelType
from darwin.sampling.sampler import Sampler
from darwin.postprocessing.validation import validate_syntax


class Server:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.app = web.Application()
        self.app.add_routes([web.get("/", self.index)])

    def start_server(self):
        web.run_app(self.app, host=self.host, port=self.port)

    async def index(self, request: web.Request) -> web.Response:
        return web.Response(text="Unimplemented")


class SamplerServer(Server):
    def __init__(
        self, host: str, port: int, backend: BackendType, model: ModelType, **kwargs
    ) -> None:
        super().__init__(host, port)
        self.app.add_routes([web.post("/sample", self.sample)])
        self.active = False
        self.last_sample_time = None
        self.n_samples = 0
        self.sampler = Sampler(backend=backend, model=model, **kwargs)

    async def index(self, request: web.Request):
        info = {
            "active": self.active,
            "last_sample": str(self.last_sample_time)
            if self.last_sample_time
            else "never",
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
        return web.json_response(
            data={"code": result, "island_id": request["island_id"]}
        )


class PostProcessorServer(Server):
    def __init__(self, host: str, port: int, verify_only: bool, **kwargs) -> None:
        super().__init__(host, port)
        self.app.add_routes([web.post("/process", self.process)])
        self.active = False
        self.last_process_time = None
        self.n_process = 0
        self.corrector = None
        if not verify_only:
            if "backend" not in kwargs:
                raise ValueError(
                    "PostProcessorServer instantiated with Corrector (verify_only = False) but `backend: BackendType` and `model: ModelType` keyword arguments not given."
                )
            self.corrector = Corrector(
                backend=kwargs["backend"], model_name=kwargs["model"], **kwargs
            )

    async def index(self, request: web.Request):
        info = {
            "active": self.active,
            "last_process": str(self.last_process_time)
            if self.last_process_time
            else "never",
            "n_process": self.n_process,
        }
        return web.json_response(data=info)

    async def process(self, request: web.Request):
        request = await request.json()
        if "code" not in request:
            return web.Response(
                text="Please specify the code to be validated through json with the key `code`"
            )
        self.n_process += 1
        self.last_process_time = datetime.now()
        code = self.parse(request["code"]) or request["code"]
        if validate_syntax(code):
            return web.json_response(data={"code": code})
        if self.corrector:
            self.last_process_time = datetime.now()
            fixed = await self.corrector.fix(code)
            self.parse(fixed)
            if validate_syntax(fixed):
                return web.json_response(data={"code": fixed})

        return web.Response(text="False")

    def parse(self, code: str):
        x = re.search(
            r"(?<!`)`{3}(?:(?!`)[^`]|\n|\r|\`(?!`))*?`{3}(?!`)", code.replace('"', "'")
        )
        # Regex Parsing
        if x:
            x = x.group(0)
            # Strip away the starting ```python and the ending ```
            x = x[x.index("def") : x.rfind("```")].strip()
            return x
        return False


class EvaluationServer(Server):
    def __init__(self, host: str, port: int, eval_function: str) -> None:
        super().__init__(host, port)
        self.app.add_routes([web.post("/evaluate", self.evaluate)])
        self.evaluator = Evaluator()
        self.eval_function = eval_function

    async def evaluate(self, request: web.Request):
        request = await request.json()
        if (
            "specification" not in request
            or "code" not in request
            or "island_id" not in request
            or "inputs" not in request
        ):
            return web.Response(
                text="Missing one or more of ['specification', 'code', 'island_id', 'inputs']",
                status=400,
            )
        score = await self.evaluator.eval(
            request["code"], request["inputs"], self.eval_function
        )
        return web.json_response(
            data={
                "score": score,
                "code": request["code"],
                "island_id": request["island_id"],
            }
        )


class EvolverServer(Server):
    def __init__(
        self, host: str, port: int, config: EvolverConfig, base_function: str
    ) -> None:
        super().__init__(host, port)
        self.app.add_routes([web.get("/getsample", self.get_prompt)])
        self.app.add_routes([web.post("/registersample", self.register_sample)])
        self.evolver = Evolver(config)
        self.evolver.populate_islands(base_function)

    async def index(self, request: web.Request):
        return web.json_response(
            data={
                "num_active_islands": len(self.evolver.active_islands_ids),
                "n_clusters": sum([len(i.clusters) for i in self.evolver.islands]),
            }
        )

    async def get_prompt(self, request: web.Request):
        prompt = "\n\n".join([s.code for s in self.evolver.get_samples()])
        return web.json_response(data={"prompt": prompt})

    async def register_sample(self, request: web.Request):
        request = await request.json()
        if "code" in request and "island_id" in request and "score" in request:
            self.evolver.register_sample(
                Sample(request["code"], request["score"]),
                [request["score"]],
                request["island_id"],
            )
        return web.Response(
            text="Missing one or more of ['code', 'island_id', 'score']"
        )
