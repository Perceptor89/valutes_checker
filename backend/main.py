from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from cbr_client.currency_loader import CurrencyLoader
from database.accessor import PostgresClient
from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class Application(FastAPI):
    db_client: PostgresClient | None = None
    templates: Jinja2Templates | None = None


@asynccontextmanager
async def lifespan(app: Application):
    app.db_client = PostgresClient()
    app.db_client.connect()
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.templates = Jinja2Templates(directory='templates')

    yield

    app.db_client.disconnect()


app = Application(lifespan=lifespan)


@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request, days_back: str = ''):
    buttons = ['today', 'yesterday', '2 days ago']
    target_valutes = ['EUR', 'USD']

    days_back = buttons.index(days_back) if days_back in buttons else 0
    date = (datetime.utcnow() - timedelta(days=days_back)).date()
    values = app.db_client.get_values(target_valutes, date)
    if not values:
        loader = CurrencyLoader()
        loader.load_data(date)
        values = app.db_client.get_values(target_valutes, date)

    values = [(char, "{:.4f}".format(value)) for char, value in values]

    return app.templates.TemplateResponse(
        'currencies.html',
        {
            'request': request,
            'date': date,
            'values': values,
            'buttons': buttons,
        }
    )
