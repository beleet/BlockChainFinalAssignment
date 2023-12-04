from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class EthereumAddress(BaseModel):
    address: str


@app.post("/receive_address")
async def receive_address(ethereum_address: EthereumAddress):
    address = ethereum_address.address

    print(f"Received Ethereum address: {address}")

    return {"message": "Address received successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
