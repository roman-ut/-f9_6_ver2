import os

from aiohttp import web

print(os.path.dirname(__file__))
WS_FILE = os.path.join(os.path.dirname(__file__), "websocket.html")


def init():
    app = web.Application()
    app["sockets"] = []
    app.router.add_get("/new", wshandler) # wshandler опишем позже
    app.on_shutdown.append(on_shutdown) # on_shutdown опишем позже
    return app


async def wshandler(request: web.Request):
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)
    try:
        print("Someone joined.")
        request.app["sockets"].append(resp)
        async for msg in resp:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)
        print("Someone disconnected.")


async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close()


web.run_app(init())
