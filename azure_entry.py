import flet as ft
from main import main

app = ft.run(main, export_asgi_app=True)
