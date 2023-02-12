import flet as ft
import InziFormOcr as formOcr
import numpy as np
from PIL import Image
import json
import base64

def main(page: ft.Page):
    page.title = "Inzisoft Form Ocr Demo"
    page.scroll = "adaptive"
    page.expand = True
    page.window_maximized = True
    page.padding = 20
    # page.theme = ft.theme.Theme(color_scheme_seed="green")

    def page_resize(e):
        c_img.height = page.window_height - 200
        c_result.height = page.window_height - 200
        result.height = page.window_height - 300
        page.update()

    page.on_resize = page_resize

    title = ft.Text("Inzisoft Form Ocr Demo", size=30, italic=True, weight=ft.FontWeight.BOLD)

    def pick_files_result(e: ft.FilePickerResultEvent):
        selected_file.value = e.files[0].name if e.files else ""
        selected_file.update()

        if selected_file.value != "":
            img.src = selected_file.value
            img.visible = True

            pr.visible = True
            update()

            image = Image.open(img.src)
            elepsed, strResult, strResultJson = formOcr.processFormOcr(
                3, "./fullText.xml", np.asarray(image))
            json_result = json.loads(strResultJson, )
            result_text.value = strResult
            result_json.value = json.dumps(json_result, indent=4, ensure_ascii=False)
            pr.visible = False
            update()

        page.update()

    selected_file = ft.Text()
    pick_file_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_file_dialog)

    bt_file = ft.ElevatedButton(
        "파일선택",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: pick_file_dialog.pick_files())

    img = ft.Image(src = None, visible = False,
        fit=ft.ImageFit.CONTAIN,)#, height=page.window_height - 200)

    result = ft.Text(selectable = True, width = 500)#, height=page.window_height - 300
    result_text = ft.Text()
    result_json = ft.Text()


    pr = ft.ProgressRing(disabled=True, visible=False)

    def tabs_changed(e):
        update()

    def update():
        status =  t.tabs[t.selected_index].text
        if status == "text":
            result.value = result_text.value
        elif status == "json":
            result.value = result_json.value
        page.update()

    t = ft.Tabs(
        selected_index = 0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="text",
            ),
            ft.Tab(
                text="json",
            )
        ],
        on_change = tabs_changed
    )

    c_img = ft.Container(img, expand=True, bgcolor=ft.colors.BLUE_GREY_900, border_radius=10, padding=20)
    c_result = ft.Container(ft.Column(controls=[t, result]), bgcolor=ft.colors.BLUE_GREY_900, border_radius = 10, padding=20)

    page.add(
        title,
        ft.Row(
            controls = [bt_file, selected_file, pr]
        ),
        ft.Row(
            controls=[c_img, c_result],
            auto_scroll = True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )
    )

ft.app(target=main)
