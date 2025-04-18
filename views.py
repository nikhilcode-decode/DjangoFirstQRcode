import os
import tempfile
import math
from datetime import datetime
import qrcode
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

def generate_status_tag(request):
    if request.method == 'POST':
        part = request.POST.get('part')
        packing_std = int(request.POST.get('packing_std'))
        qty = int(request.POST.get('qty'))  # Convert quantity to an integer
        tag_type = request.POST.get('tag_type')  # Get the tag type (9 or 18)

        # Create an HTTP response with the PDF content
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "inline; filename=VeeGee_QR.pdf"

        # Initialize PDF canvas and page size variables based on tag type (9 or 18)
        if tag_type == "9":
            # For 9 tags layout, use A3 in landscape mode (42 cm x 29.7 cm)
            page_width, page_height = landscape(A3)
        else:
            # For 18 tags layout, use A3 in portrait mode (29.7 cm x 42 cm)
            page_width, page_height = A3

        # Create PDF canvas
        pdf = canvas.Canvas(response, pagesize=(page_width, page_height))

        # Path to the "Zero Defect" image
        zero_defect_path = os.path.join(os.path.dirname(__file__), "static/zero_defect.png")

        # Function to generate a QR code as an image
        def generate_qr_code(data):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')
            # Save the image to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            img.save(temp_file, format='PNG')
            temp_file.close()  # Ensure it's saved before using it
            return temp_file.name  # Return the file path

        # Function to draw a single tag for 9 tags layout (A3 Landscape)
        def draw_tag_9(pdf, x, y, unique_number, part, packing_std="none", qty="none"):
            # Get current date & time
            current_datetime = datetime.now().strftime("%d-%m-%y ~ %H:%M:%S")
            part_no = part.upper()

            # Tag Border;
            pdf.rect(x, y, 12.5 * cm, 8.5 * cm)  # Adjust the size of each tag for 9 tags

            # Header Section
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(x + 0.3 * cm, y + 7.8 * cm, "IDENTIFICATION / STATUS TAG")
            pdf.drawString(x + 0 * cm, y + 7.5 * cm, "_____________________________________________________")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(x + 8 * cm, y + 7.8 * cm, f"Date : ")

            # Part Details
            pdf.drawString(x + 0.3 * cm, y + 7 * cm, f"Part : {part_no}")
            pdf.drawString(x + 0.3 * cm, y + 6.4 * cm, "Trolley No : ")
            pdf.drawString(x + 0.3 * cm, y + 5.8 * cm, "Name: PANEL COMP, FENDER APRON, R")
            pdf.drawString(x + 8 * cm, y + 7 * cm, "Model : ")
            pdf.drawString(x + 8 * cm, y + 6.4 * cm, "Qty : ")

            # Generate and place QR Code
            qr_code_data = f"{part_no}~{packing_std}~{current_datetime}~{str(unique_number).zfill(3)}"
            qr_code_path = generate_qr_code(qr_code_data)
            pdf.drawImage(qr_code_path, x + 5.9 * cm, y + 2.55 * cm, width=3 * cm, height=3 * cm)

            # Add "Zero Defect" image
            if os.path.exists(zero_defect_path):
                pdf.drawImage(zero_defect_path, x + 9.0 * cm, y + 2.8 * cm, width=3 * cm, height=2.5 * cm, mask='auto')

            # Inspector Names Section
            pdf.setFont("Helvetica", 9)
            pdf.drawString(x + 0 * cm, y + 2.5 * cm, "_______________________________________________________________________")
            pdf.drawString(x + 0.3 * cm, y + 2.0 * cm, "PDI Inspector Name : ")
            pdf.drawString(x + 0 * cm, y + 1.7 * cm, "_______________________________________________________________________")
            pdf.drawString(x + 0.3 * cm, y + 1.2 * cm, "Tagger Name : ")
            pdf.drawString(x + 0 * cm, y + 0.90 * cm, "_______________________________________________________________________")
            pdf.drawString(x + 0.3 * cm, y + 0.40 * cm, "Checker Name : ")

        # Function to draw a single tag for 18 tags layout (A3 Portrait)
        def draw_tag_18(pdf, x, y, unique_number, part, packing_std="none", qty="none"):
            # Get current date & time
            current_datetime = datetime.now().strftime("%d-%m-%y ~ %H:%M:%S")
            part_no = part.upper()

            # Border
            pdf.rect(x, y, 9 * cm, 6 * cm)  # Adjust the size of each tag for 18 tags

            # Header Section
            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawString(x + 0.1 * cm, y + 5.5 * cm, "IDENTIFICATION / STATUS TAG")
            pdf.setFont("Helvetica", 8)
            pdf.drawString(x + 0 * cm, y + 5.3 * cm, "_________________________________________________________")
            pdf.setFont("Helvetica", 10)
            pdf.drawString(x + 6.3 * cm, y + 5.5 * cm, f"Date : ")

            # Part Details
            pdf.setFont("Helvetica", 8)
            pdf.drawString(x + 0.1 * cm, y + 4.9 * cm, f"Part : {part_no}")
            pdf.drawString(x + 0.1 * cm, y + 4.4 * cm, "Trolley No : ")
            pdf.drawString(x + 0.1 * cm, y + 3.9 * cm, "Name: PANEL COMP, FENDER APRON, R")
            pdf.drawString(x + 6.3 * cm, y + 4.9 * cm, "Model : ")
            pdf.drawString(x + 6.3 * cm, y + 4.4 * cm, "Qty : ")

            # Generate and place QR Code
            qr_code_data = f"{part_no}~{packing_std}~{current_datetime}~{str(unique_number).zfill(3)}"
            qr_code_path = generate_qr_code(qr_code_data)
            pdf.drawImage(qr_code_path, x + 3.8 * cm, y + 1.3 * cm, width=2.5 * cm, height=2.5 * cm)

            # Add "Zero Defect" image
            if os.path.exists(zero_defect_path):
                pdf.drawImage(zero_defect_path, x + 6.2 * cm, y + 1.6 * cm, width=2.5 * cm, height=2.0 * cm, mask='auto')

            # Inspector Names Section
            pdf.setFont("Helvetica", 7)
            pdf.drawString(x + 0 * cm, y + 1.5 * cm, "_________________________________________________________________")
            pdf.drawString(x + 0.1 * cm, y + 1.07 * cm, "PDI Inspector Name : ")
            pdf.drawString(x + 0 * cm, y + 1.0 * cm, "_________________________________________________________________")
            pdf.drawString(x + 0.1 * cm, y + 0.6 * cm, "Tagger Name : ")
            pdf.drawString(x + 0 * cm, y + 0.5 * cm,"_________________________________________________________________")
            pdf.drawString(x + 0.1 * cm, y + 0.1 * cm, "Checker Name : ")

        # Initialize unique_number before the loop starts
        unique_number = 1  # Start with 001, 002, etc.

        # Define starting position and offsets dynamically based on tag type (9 or 18 tags)
        if tag_type == "9":
            # 9 tags per page: 3x3 grid (Landscape mode)
            x_start, y_start = 1.4 * cm, page_height - 9.5 * cm  # Starting position for 9 tags
            x_offset, y_offset = 13.5 * cm, 9.5 * cm  # Offsets between tags for 9 tags
        else:
            # 18 tags per page: 6x3 grid (A3 Portrait)
            x_start, y_start = 0.8 * cm, page_height - 6.8 * cm  # Starting position for 18 tags
            x_offset, y_offset = 9.7 * cm, 6.9 * cm  # Distribute space evenly (9 cm width, 6.5 cm height per tag)

        # Calculate how many pages are needed
        if tag_type == "9":
            num_pages = math.ceil(qty / 9)  # Each page holds 9 tags
        else:
            num_pages = math.ceil(qty / 18)  # Each page holds 18 tags

        # Arrange tags in a grid
        for page in range(num_pages):
            # For each page, generate tags
            if page > 0:  # Create a new page if it's not the first page
                pdf.showPage()

            # Draw the tags on the current page
            if tag_type == "9":
                for i in range(min(9, qty - page * 9)):  # Only draw the remaining tags
                    row = i // 3  # Calculate row index
                    col = i % 3  # Calculate column index
                    draw_tag_9(pdf, x_start + col * x_offset, y_start - row * y_offset, unique_number, part, packing_std)
                    unique_number += 1  # Increment unique_number for the next tag
            elif tag_type == "18":
                for i in range(min(18, qty - page * 18)):  # Only draw the remaining tags
                    row = i // 3  # Calculate row index
                    col = i % 3  # Calculate column index
                    draw_tag_18(pdf, x_start + col * x_offset, y_start - row * y_offset, unique_number, part, packing_std)
                    unique_number += 1  # Increment unique_number for the next tag

        # Finalize the PDF
        pdf.save()
        return response

    else:
        return render(request, 'tag_generator/status_tag_form.html')


