from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import database


app = FastAPI()
templates = Jinja2Templates(directory="templates")


class SubscriptionForm(BaseModel):
    ethereum_address: str


@app.get("/channel/{channel_index}")
async def read_channel(channel_index: int, request: Request):
    channel_info = database.channels[channel_index]
    if not channel_info:
        return {"error": "Канал не найден"}

    return templates.TemplateResponse(
        "channel_info.html",
        {"request": request, "channel_info": channel_info, "channel_index": channel_index},
    )


@app.post("/subscribe/{channel_index}")
async def subscribe_to_channel(channel_index: int, form_data: SubscriptionForm):
    ethereum_address = form_data.ethereum_address

    return {"message": f"Вы подписались на канал {channel_index} с адресом {ethereum_address}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
