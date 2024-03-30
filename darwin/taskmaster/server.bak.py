import asyncio
import time
from collections import deque
from aiohttp import web

routes = web.RouteTableDef()


# General information about the current Darwin state
@routes.get("/")
async def status(request):
    request.app["queue"].append(1)
    return web.json_response(
        data={
            "task_queue": [i for i in request.app["queue"]],
            "server_alive_length": time.time() - request.app["start_time"],
        }
    )


# Task Handling
@routes.post("/complete")
async def on_task_finish(request):
    request = await request.json()
    return web.Response(status=200)


async def start_queue_loop(app):
    app["queue"] = deque()
    asyncio.create_task(process_queue(app))


async def process_queue(app):
    while True:
        await asyncio.sleep(1)
        print(len(app["queue"]))


def main():
    app = web.Application()
    app.add_routes(routes)
    app["start_time"] = time.time()
    app.on_startup.append(start_queue_loop)
    web.run_app(app)


if __name__ == "__main__":
    main()
