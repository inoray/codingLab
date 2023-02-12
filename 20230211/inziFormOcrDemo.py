import flet as ft
import InziFormOcr as formOcr
import numpy as np
from PIL import Image
import json
import base64

def main(page: ft.Page):
    page.title = "Inzisoft Form Ocr Demo"
    page.scroll = "adaptive"
    page.theme = ft.theme.Theme(color_scheme_seed="green")

    def page_resize(e):
        img.height = page.window_height - 200
        # print("New page size:", page.window_width, page.window_height)
        result.height = page.window_height - 300
        img.update()
    page.on_resize = page_resize

    title = ft.Text("Inzisoft Form Ocr Demo", size=30, italic=True, weight=ft.FontWeight.BOLD)

    def pick_files_result(e: ft.FilePickerResultEvent):
        selected_file.value = e.files[0].name if e.files else ""
        selected_file.update()

        if selected_file.value != "":
            img.src = selected_file.value

            image = Image.open(img.src)
            elepsed, strResult, strResultJson = formOcr.processFormOcr(
                3, "./fullText.xml", np.asarray(image))
            json_result = json.loads(strResultJson, )
            result_text.value = strResult
            result_json.value = json.dumps(json_result, indent=4, ensure_ascii=False)
            update()

        page.update()

    selected_file = ft.Text()
    pick_file_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_file_dialog)

    bt_file = ft.ElevatedButton(
        "파일선택",
        icon=ft.icons.UPLOAD_FILE,

        on_click=lambda _: pick_file_dialog.pick_files())

    img = ft.Image(src = None,
        fit=ft.ImageFit.CONTAIN, height=page.window_height - 200)

    result = ft.Text(selectable = True, height=page.window_height - 300)
    result_text = ft.Text(selectable = True)
    result_json = ft.Text(selectable=True)


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
                # content=result_text
            ),
            ft.Tab(
                text="json",
                # content=result_json
            )
        ],
        on_change = tabs_changed
    )

    page.add(
        title,
        ft.Row(
            controls = [bt_file, selected_file]),
        ft.Row(
            controls=[img,
                      ft.Column(
                          controls=[t, result]
                          )
                ],

            auto_scroll = True,
            vertical_alignment=ft.CrossAxisAlignment.START
            )


    )

ft.app(target=main)
