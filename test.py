from darwin.client import DarwinClient
from darwin.configuration import (
    DarwinConfig,
    EvaluationConfig,
    EvolverConfig,
    PostProcessConfig,
    SpecParseConfig,
    SampleConfig,
)
from darwin.sampling.backend import BackendType
from darwin.sampling.models import ModelType


with open("./sentence_specification.py", "r") as f:
    spec = f.read()


config = DarwinConfig(
    sample_config=SampleConfig(
        model_distribution={ModelType.deepseekcoder67: 0.75, ModelType.gemma: 0.25},
        backend=BackendType.ollama,
        ollama_server_address="http://127.0.0.1:11434",
        n_samplers=8,
    ),
    spec_parse_config=SpecParseConfig(
        evolved_function_name="priority", solver_function_name="evaluate"
    ),
    postprocess_config=PostProcessConfig(
        n_postprocessors=4,
        correct_samples=True,
        model_distribution={ModelType.llama2: 1},
    ),
    evaluation_config=EvaluationConfig(n_evaluators=16, sanbox=False),
    evolve_config=EvolverConfig(),
)

client = DarwinClient(spec, config=config)

client.start_evolution()
