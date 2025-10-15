import flet as ft

def main(page: ft.Page):
    page.title = "Previsão de Violência no Brasil"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Column([
            ft.Text("Interface de Análise e Previsão", size=30, weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)