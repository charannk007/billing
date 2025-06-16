import os
from barcode import get_barcode_class
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import logging

def generate_barcode(product_id, product_name, price):
    try:
        output_dir = 'static/barcodes'
        os.makedirs(output_dir, exist_ok=True)

        # Barcode settings
        barcode_class = get_barcode_class('code128')
        if not barcode_class:
            raise ValueError("Failed to load Code128 barcode class")
        
        writer_options = {
            'module_width': 0.2,  # mm, reduced for smaller label
            'module_height': 10.0,  # mm, fits 1" height
            'quiet_zone': 2.0,  # Reduced for smaller label
            'font_size': 0,
            'dpi': 300,
            'write_text': False,
            'format': 'PNG'
        }

        # Generate and save raw barcode
        raw_path = os.path.join(output_dir, f"{product_id}_raw")
        barcode = barcode_class(str(product_id), writer=ImageWriter())
        barcode.save(raw_path, options=writer_options)
        barcode_img = Image.open(f"{raw_path}.png")

        # Label size: 2" x 1" at 300 DPI = 600x300 pixels
        label_width, label_height = 600, 300
        final_img = Image.new("RGB", (label_width, label_height), "white")
        draw = ImageDraw.Draw(final_img)

        # Load fonts
        try:
            header_font = ImageFont.truetype("arial.ttf", 30)  # Smaller font for header
            footer_font = ImageFont.truetype("arial.ttf", 20)  # Smaller font for footer
        except IOError:
            logging.warning("Arial font not found, using default font")
            header_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Draw store name
        store_text = "Charan Super Market"
        store_bbox = draw.textbbox((0, 0), store_text, font=header_font)
        store_w, store_h = store_bbox[2] - store_bbox[0], store_bbox[3] - store_bbox[1]
        draw.text(((label_width - store_w) // 2, 10), store_text, fill="black", font=header_font)

        # Paste barcode
        barcode_y = 60  # Adjusted for smaller label
        if barcode_img.height > label_height - barcode_y - 60:  # Reserve space for text
            raise ValueError("Barcode too tall for label")
        x_offset = (label_width - barcode_img.width) // 2
        final_img.paste(barcode_img, (x_offset, barcode_y))

        # Draw product name and price
        label_text = f"{product_name} ₹{price}"
        text_bbox = draw.textbbox((0, 0), label_text, font=footer_font)
        text_w, text_h = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        bottom_y = barcode_y + barcode_img.height + 10
        if bottom_y + text_h < label_height:
            draw.text(((label_width - text_w) // 2, bottom_y), label_text, fill="black", font=footer_font)
        else:
            raise ValueError("Text does not fit on label")

        # Save final label
        final_path = os.path.join(output_dir, f"{product_id}.png")
        final_img.save(final_path, quality=95)

        # Clean up raw barcode file
        os.remove(f"{raw_path}.png")

        return final_path

    except Exception as e:
        logging.error(f"Error generating barcode: {str(e)}")
        raise
