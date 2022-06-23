# main.py
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from pypsrp.client import Client
from dnshelper import add_dns_record, delete_dns_record
import uvicorn
from logging.config import dictConfig
import logging
from config import LogConfig
import os
import secrets

# Logging config
dictConfig(LogConfig().dict())
logger = logging.getLogger("windnsapi")

app = FastAPI()
security = HTTPBasic()

server = os.getenv('WIN_SRV_HOST')
user = os.getenv('WIN_SRV_USERNAME')
password = os.getenv('WIN_SRV_PASSWORD')


# pydantic class for Add Record
class AddRecord(BaseModel):
    zone: str
    host: str
    ip: str


# pydantic class for Add Record
class DelRecord(BaseModel):
    zone: str
    host: str


# Security service class
class SecurityService:
    def __init__(self):
        self.username = os.getenv('BASIC_AUTH_USERNAME')
        self.password = os.getenv('BASIC_AUTH_PASSWORD')

    def verify(self, credentials):
        correct_credentials = secrets.compare_digest(credentials.username + credentials.password,
                                                     self.username + self.password)
        if not correct_credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )


# test endpoint
@app.get("/api/")
async def root(credentials: HTTPBasicCredentials = Depends(security)):
    SecurityService().verify(credentials)
    return {"message": "It works!"}


# add record endpoint
@app.post("/api/record", status_code=201)
async def add_record(recordset: AddRecord, credentials: HTTPBasicCredentials = Depends(security)):
    SecurityService().verify(credentials)
    zone = recordset.zone
    host = recordset.host
    ip = recordset.ip
    logger.info(f'Received request to add A record for host "{host}" mapped to "{ip}" in "{zone}" zone')
    with Client(server, username=user, password=password, ssl=False) as client:
        logger.info(f'Starting record addition...')
        result = add_dns_record(client, zone, host, ip)
        if not result:
            raise HTTPException(status_code=404, detail="Record creation failed")
        return {
            "status": "SUCCESS",
            "data": recordset
        }


# delete record endpoint
@app.delete("/api/record", status_code=200)
async def delete_record(recordset: DelRecord, credentials: HTTPBasicCredentials = Depends(security)):
    SecurityService().verify(credentials)
    zone = recordset.zone
    host = recordset.host
    logger.info(f'Received request to delete A record for host "{host}" in "{zone}" zone')
    with Client(server, username=user, password=password, ssl=False) as client:
        logger.info(f'Starting record deletion...')
        result = delete_dns_record(client, zone, host)
        if not result:
            raise HTTPException(status_code=404, detail="Record deletion failed")
        return {
            "status": "SUCCESS",
            "data": recordset
        }


if __name__ == '__main__':
    uvicorn.run("main:app", port=443, host='0.0.0.0', ssl_certfile="./cert.pem", ssl_keyfile="./key.pem")

