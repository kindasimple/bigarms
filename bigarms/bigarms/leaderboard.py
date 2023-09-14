import time

from actionlog import actionlog
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mangum import Mangum

app = FastAPI()

app.mount("/static", StaticFiles(directory="bigarms/static"), name="static")
templates = Jinja2Templates(directory="bigarms/templates")


def timectime(s):
    return time.ctime(s)  # datetime.datetime.fromtimestamp(s)


templates.env.filters["ctime"] = timectime


@app.get("/", response_class=HTMLResponse)
async def statistics(request: Request):
    summaries = actionlog.get_summary(action="pushups")
    context = {"request": request, "summaries": summaries}
    return templates.TemplateResponse("leaderboard.html", context)


# @app.get("/api", response_class=HTMLResponse)
# @app.get("/api/{action}", response_class=HTMLResponse)
# async def read_root(request: Request, action='pushups'):
#     summaries = actionlog.get_summary(action)
#     return JSONResponse(content=jsonable_encoder(summaries))


# @app.get("/summary/{action}")
# async def read_item(action: str):
#     return actionlog.get_summary(action)

handler = Mangum(app)
