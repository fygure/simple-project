from pydantic import BaseModel, AnyUrl, Field
from typing import Union, Optional, Dict
from fastapi import FastAPI
from flask import Flask
import logging

class Logger(BaseModel):
    name: str = "default_logger"
    level: int = logging.INFO

class ObserverResourceModel(BaseModel):
    datadog_endpoint: AnyUrl
    logger_obj: Logger = Logger()
    app: Union[FastAPI, Flask]
    app_env: str = "local"
    is_local: bool = True
    version: str = "1.0.0"
    additional_info: Optional[Dict[str, str]] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class ObserverResource:
    # Constructor
    def __init__(self, resource_data: ObserverResourceModel):
        self.datadog_endpoint = resource_data.datadog_endpoint
        self.logger_obj = self._init_logger(resource_data.logger_obj)
        self.app = resource_data.app
        self.app_env = resource_data.app_env
        self.is_local = resource_data.is_local
        self.version = resource_data.version
        self.additional_info = resource_data.additional_info
        self.app_type = self._determine_app_type(resource_data.app)
        
    @staticmethod
    def _init_logger(logger_data: Logger) -> logging.Logger:
        logger = logging.getLogger(logger_data.name)
        logger.setLevel(logger_data.level)
        return logger
    
    @staticmethod
    def _determine_app_type(app: Union[FastAPI, Flask]) -> str:
        if isinstance(app, FastAPI):
            return "FastAPI"
        elif isinstance(app, Flask):
            return "Flask"
        else:
            raise ValueError("Unsupported app type. Only FastAPI and Flask are supported.")
        
    @classmethod
    def edit_options(cls, resource: ObserverResourceModel, **kwargs):
        for key, value in kwargs.items():
            if hasattr(resource, key):
                setattr(resource, key, value)
            else:
                raise AttributeError(f"'Resource' object has no attribute '{key}'")
        return resource

    def __repr__(self):
        return (f"Resource(datadog_endpoint={self.datadog_endpoint}, "
                f"logger_obj={self.logger_obj}, app={self.app}, app_env={self.app_env}, "
                f"is_local={self.is_local}, version={self.version}, additional_info={self.additional_info})")

# Example usage with Pydantic
resource_data = ObserverResourceModel(
    datadog_endpoint="https://api.datadoghq.com",
    logger_obj=Logger(name="my_logger", level=logging.DEBUG),
    app=FastAPI(),
    app_env="development",
    is_local=True,
    version="1.0.0",
    additional_info={"additional_attr1": "value1", "additional_attr2": "value2"}
)

resource = ObserverResource(resource_data)
print(resource)

# Example of editing options
resource = ObserverResource.edit_options(resource,
    datadog_endpoint="https://new.api.datadoghq.com",
    app_env="production"
)
print(resource)
