
import barcode
from barcode.writer import ImageWriter
import os

def generate_barcode(item_id):
    if not os.path.exists('static/barcodes'):
        os.makedirs('static/barcodes')
    code = barcode.get('code128', str(item_id), writer=ImageWriter())
    filename = f'static/barcodes/{item_id}'
    code.save(filename)
    return f'barcodes/{item_id}.png'
