from quart import Quart, render_template, Response
from parser import get_resources
from remnawave_api import remna
from remnawave.exceptions import NotFoundError
from httpx import AsyncClient
from config import *
import asyncio


app = Quart(__name__)


client = AsyncClient(headers={
    "Authorization": "Bearer "+REMNA_TOKEN
})


logs_content = ""
async def background_file_reader():
    global logs_content
    while True:
        try:
            with open(ACCESS_LOGS, "r", encoding="utf-8") as f:
                logs_content = f.read()
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
        await asyncio.sleep(1)


@app.before_serving
async def start_background_task():
    app.add_background_task(background_file_reader)


@app.get(f"/{WEBAPP_SECRET}/<short_uuid>")
async def index(short_uuid: str):
    try:
        remna_user = await remna.users.get_user_by_short_uuid(short_uuid)
    except NotFoundError:
        return Response(status=404)
    else:
        request_url = REMNA_URL + "/api/users/" + remna_user.uuid
        remna_user_response = await client.get(request_url)
        remna_user_id = remna_user_response.json()["id"]
        sites = await get_resources(logs_content, remna_user_id)
        return await render_template("index.html", sites=sites)


async def run_webapp():
    await app.run_task("0.0.0.0", 8080, True)
