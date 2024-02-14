# -*- coding: utf-8 -*-
import os
from fastapi import Request
from fastapi.templating import Jinja2Templates
from modules import paths

templates = Jinja2Templates(directory=os.path.join(paths.DIR_ROOT, "templates"))


def render(request: Request, name: str, context: dict = {}):
    return templates.TemplateResponse(request=request, name=name, context=context)
