from fastapi import FastAPI
from info import APP_NAME, APP_SUMMARY, APP_VERSION, APP_CONTACT
from backend.account import account_router
from backend.data import data
from fastapi.responses import JSONResponse
from constants.api_endpoints.account import ACCOUNT_ROUTER
from constants.api_endpoints.data import DATA_ROUTER
from mangum import Mangum
from dbchecker import DbChecker
DB_CHECKER = "/check-db"
app = FastAPI(
    title=APP_NAME,
    # description=app_description,
    summary=APP_SUMMARY,
    version=APP_VERSION,
    contact=APP_CONTACT,
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}
    )
@app.post(DB_CHECKER, include_in_schema=True)
def db_checker():
    """Check for table and create them."""
    return JSONResponse(content=DbChecker().execute(), status_code=201)

app.include_router(account_router, prefix=ACCOUNT_ROUTER)
app.include_router(data, prefix=DATA_ROUTER)
handler = Mangum(app=app)
