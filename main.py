from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
app = FastAPI()

@app.get("/{sport}/{year}/{month}")
def main(month, year, sport):
    def iterfile():  #
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import Table, TableStyle
        from firebase_admin import credentials, initialize_app, db
        from datetime import datetime
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Initialize Firebase
        cred = credentials.Certificate("fs.json")
        initialize_app(cred, {
            'databaseURL': "https://frontline-sport-default-rtdb.firebaseio.com"
        })
                        # Register fonts
        pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSerif.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSM', 'DejaVuSansMono.ttf'))

        # Create a canvas object
        c = canvas.Canvas("example.pdf", pagesize=letter)
        width, height = letter

        # Set the font for the canvas
        c.setFont("Helvetica", 12)

        # Draw "Frontline Sport UA"
        c.drawString(50, height - 50, "Frontline Sport UA")

        # Draw "MMA"
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 70, "MMA")

        # Draw "03-2024"
        c.setFont("Helvetica", 12)
        c.drawString(width - 90, height - 50, "03-2024")

        # Read data from the database
        data = db.reference('/').get()

        # Prepare table data
        usrs = ["0"]
        tb_data = [["User"]]
        for u in data["users"]:
            if sport in data["users"][u]['dir']:
                usrs.append(u)

        for i in data[sport]["trainings"]:
            date_object = datetime.strptime(i[0:10], '%Y-%m-%d')
            a = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
            dt = str(date_object).split(" ")[0].split("-")[::-1]
            if dt[1] == month:
                date = f'{a[date_object.weekday()]}\n{dt[0]}'
                tb_data[0].append(str(date))

        for u in usrs:
            if u == "0":
                pass
            else:
                tb_data.append([u])
                try:
                    for i in data[sport]["trainings"]:
                        tb_data[usrs.index(u)].append(
                            "+" if data["users"][u]["id"] in data[sport]["trainings"][i]["present"] else "-")
                except:
                    tb_data[usrs.index(u)].append("-")

        # Create table
        table = Table(tb_data)
        style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Align first column to the left
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),  # Align other columns to the center
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSM'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSM'),  # Apply font to table content
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        table.setStyle(style)

        # Draw table below "MMA"
        table.wrapOn(c, width, height)
        table.drawOn(c, 50, height - 28 * len(usrs))

        # Save the PDF
        c.drawString(50, 20, "frontline-stats.pages.dev")
        c.save()
        some_file_path = "example.pdf"



        with open(some_file_path, mode="rb") as file_like:  #
            yield from file_like  #

    return StreamingResponse(iterfile(), media_type="image.pdf")
