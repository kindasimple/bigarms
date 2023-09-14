import time

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from mangum import Mangum
from bigarms.actionlog import actionlog

app = FastAPI()

templates = Jinja2Templates(directory="templates")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def timectime(s):
    return time.ctime(s) # datetime.datetime.fromtimestamp(s)


templates.env.filters['ctime'] = timectime


@app.get("/", response_class=HTMLResponse)
async def statistics(request: Request):
    action = 'pushups'
    summaries = actionlog.get_summary(action)
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