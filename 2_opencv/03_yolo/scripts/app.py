import sqlite3
import gradio as gr
import io
import os
import base64
from datetime import datetime, timedelta
from convertdate import persian
from PIL import Image, ImageEnhance
from detection import run_detection

DB_PATH = "./Database/screeb.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS number_plates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate BLOB NOT NULL,
    entry_time TEXT NOT NULL,
    exit_time TEXT
);
''')
conn.commit()

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def gregorian_to_persian_string(gregorian_str):
    dt = datetime.strptime(gregorian_str, "%Y-%m-%d %H:%M:%S")
    y, m, d = persian.from_gregorian(dt.year, dt.month, dt.day)
    return f"{y}-{m:02d}-{d:02d} {dt.strftime('%H:%M:%S')}"

def fetch_data_by_days(days):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    start_date = datetime.now() - timedelta(days=days)
    cursor.execute("""
        SELECT id, plate, entry_time, exit_time FROM number_plates
        WHERE entry_time >= ?
    """, (start_date.strftime('%Y-%m-%d %H:%M:%S'),))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return gr.update(value="<p style='color:red; background_color:gray;'>هیچ دیتایی در این تاریخ  یافت نشد.</p>")
    return render_table(rows)

def search_by_id(search_id):
    if not search_id.strip().isdigit():
        return gr.update(value="<p style='color:red;'>لطفاً یک آی‌دی معتبر وارد کنید.</p>")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, plate, entry_time, exit_time FROM number_plates WHERE id = ?", (search_id,))
    row = cursor.fetchone()
    conn.close()
    return render_table([row]) if row else gr.update(value=f"<p style='color:red; backgournd_color:gray'>آی‌دی {search_id} یافت نشد.</p>")

def render_table(rows):
    table_html = """
    <style>
        body {
            direction: rtl;
            font-family: 'Tahoma', sans-serif;
            background-color: #f7f9fc;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 15px;
            direction: rtl;
        }
        th {
            background: lightblue;
            text-align: right;
            color: #333;
            padding: 12px;
            border: 1px solid #ccc;
            font-weight: bold;
        }
        td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: center;
            color: #333;
        }
        tr:nth-child(even) {
            background-color: #fefefe;
        }
        tr:nth-child(odd) {
            background-color: #f2f7fa;
        }
        img {
            max-height: 60px;
            border-radius: 5px;
            cursor: pointer;
            transition: 0.2s;
        }
        img:hover {
            transform: scale(1.34);
        }

        .close {
            position: absolute;
            top: 30px;
            right: 45px;
            color: green;
            font-size: 40px;
            cursor: pointer;
        }
        .close:hover {
            color: #bbb;
        }

        /* Buttons & Header */
        .gr-button {
            background: linear-gradient(to right, #74ebd5, #9face6);
            color: #000;
            border-radius: 10px;
            padding: 10px 16px;
            font-weight: bold;
            font-size: 14px;
            border: 1px solid #aaa;
            transition: background 0.3s ease-in-out;
        }
        .gr-button:hover {
            background: linear-gradient(to right, #9face6, #74ebd5);
        }

        h2 {
          
            color: white;
            padding: 14px;
            border-radius: 12px;
            text-align: center;
            font-size: 20px;
        }

        .searchbox input {
            direction: rtl !important;
            text-align: right !important;
        }
    </style>

    <table>
        <tr>
            <th>آی‌دی</th>
            <th>تصویر پلیت</th>
            <th>زمان ورود</th>
            <th>زمان خروج</th>
        </tr>
    """

    for _id, blob, entry, exit in rows:
        img = Image.open(io.BytesIO(blob))
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        entry_dt = datetime.strptime(entry, "%Y-%m-%d %H:%M:%S")
        exit_dt = datetime.strptime(exit, "%Y-%m-%d %H:%M:%S") if exit else None

        y1, m1, d1 = persian.from_gregorian(entry_dt.year, entry_dt.month, entry_dt.day)
        entry_formatted = f"{y1:04d}-{m1:02d}-{d1:02d} | {entry_dt.strftime('%H:%M:%S')}"

        if exit_dt:
            y2, m2, d2 = persian.from_gregorian(exit_dt.year, exit_dt.month, exit_dt.day)
            exit_formatted = f"{y2:04d}-{m2:02d}-{d2:02d} {exit_dt.strftime('%H:%M:%S')}"
        else:
            exit_formatted = "نامشخص"

        table_html += f"""
        <tr>
            <td>{_id}</td>
            <td><img src='data:image/jpeg;base64,{img_base64}' onclick="enlargeImage('{img_base64}')"/></td>
            <td>{entry_formatted}</td>
            <td>{exit_formatted}</td>
        </tr>
        """

    table_html += "</table>"
    return gr.update(value=table_html)


# ------------------------- UI --------------------------
gui = gr.Blocks(css="""
.gr-block { direction: ltr; font-family: sans-serif; }
.gr-button {
    background: linear-gradient(to right, #74ebd5, #9face6);
    color: #000;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #aaa;
}
.gr-button:hover {
    background: linear-gradient(to right, #9face6, #74ebd5);
}
h2 {
    background: linear-gradient(to right, #00c6ff, #0072ff);
    color: white;
    padding: 14px;
    border-radius: 12px;
    text-align: center;
}
.searchbox input {
    background:gray;
    direction: rtl !important;
    text-align: right !important;
}
""")

with gui:
    gr.Markdown("""
    <div style="text-align:center;padding: 10px; background: linear-gradient(to right,rgb(26, 35, 240));direction:rtl;">
        <h2 style='color:white; font-size:20;'> سیستم تشخیص نمبر پلیت وسایط افعانستان</h2>
        <p  style='color:white; font-size:18;'>مشاهده و جستجوی ورود/خروج نمبر پلیت‌ها</p>
    </div>
    """)

    with gr.Row():
        run_btn = gr.Button("شناسایی نمبر پلیت")
        last_week_btn = gr.Button("هفته گذشته")
        last_2_weeks_btn = gr.Button("دو هفته گذشته")
        last_3_weeks_btn = gr.Button("سه هفته گذشته ")
        show_all_btn = gr.Button("نمایش همه")

    with gr.Row():
        search_box = gr.Textbox(label="جستجو بر اساس آی‌دی")

    table_output = gr.HTML()

    run_btn.click(run_detection, outputs=[])
    last_week_btn.click(lambda: fetch_data_by_days(7), outputs=table_output)
    last_2_weeks_btn.click(lambda: fetch_data_by_days(14), outputs=table_output)
    last_3_weeks_btn.click(lambda: fetch_data_by_days(21), outputs=table_output)
    show_all_btn.click(lambda: fetch_data_by_days(1000), outputs=table_output)
    search_box.submit(search_by_id, inputs=search_box, outputs=table_output)

gui.launch(debug=True)
