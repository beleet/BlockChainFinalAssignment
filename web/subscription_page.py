from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import config

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class EthereumAddress(BaseModel):
    address: str


@app.get("/register/{business_address}")
async def receive_address(
        request: Request,
        business_address: str,
):

    contract_data = {
        'business_address': business_address,
        'master_contract_address': config.MASTER_CONTRACT_MUMBAI_ADDRESS,
    }

    return templates.TemplateResponse(
        name='register_instance_contract.html',
        context={
            'request': request,
            'data': contract_data,
        },
    )


@app.get('/transfer/{method}/{instance_contract}/{escrow_contract}/{token}/{amount}')
async def subscribe(
        request: Request,
        token: str,
        instance_contract: str,
        escrow_contract: str,
        method: str,
        amount: int,
):
    contract_data = {
        'token': token,
        'instance_contract': instance_contract,
        'escrow_contract': escrow_contract,
        'amount': amount,
        'method': method,
    }

    return templates.TemplateResponse(
        name='subscribe.html',
        context={
            'request': request,
            'data': contract_data,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
