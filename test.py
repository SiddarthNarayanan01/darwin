from multiprocessing import Process
from darwin.sampling.backend import BackendType
from darwin.sampling.models import ModelType
from darwin.taskmaster.server import SamplerServer


def init_server(server_addr, server_port):
    server = SamplerServer(
        host=server_addr,
        port=server_port,
        backend=BackendType.llamacpp,
        model=ModelType.dsc67,
        model_weights_path="./model_weights/deepseek-math-7b-rl.Q8_0.gguf"
    )
    server.start_server()


if __name__ == "__main__":
    p = Process(target=init_server, args=("localhost", 8080))
    p.start()
    p.join()

