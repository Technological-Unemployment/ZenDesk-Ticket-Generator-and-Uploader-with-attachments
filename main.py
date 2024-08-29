import os
import tempfile
import logging
import datetime
import pandas as pd
import psycopg2 as pg
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image
from pdf2image import convert_from_path
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_TOKEN = os.getenv("ZENDESK_TOKEN")
ZENDESK_SUBDOMAIN = os.getenv("ZENDESK_SUBDOMAIN")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# API base URL
ZENDESK_API_URL = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2"

def create_db_connection():
    try:
        return pg.connect(**DB_CONFIG)
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        return None

def query_data(query):
    try:
        with create_db_connection() as connection:
            df = pd.read_sql_query(query, con=connection)
        return df
    except Exception as e:
        logger.error(f"Failed to execute query: {e}")
        return None

def create_trend_chart(df, variable, save_path):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['date'], df[variable], marker='o')
    plt.title(f"Trend Chart - {variable}")
    plt.xlabel("Date")
    plt.ylabel(variable)
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Trend chart saved to {save_path}")

def create_density_plot(df, save_path):
    with PdfPages(save_path) as pdf:
        sns.set_style("whitegrid")
        sns.kdeplot(df['x'], df['y'], cmap="Reds", shade=True)
        plt.title("Density Plot")
        pdf.savefig()
        plt.close()
    logger.info(f"Density plot saved to {save_path}")

def append_pdfs(input_pdfs, output_pdf):
    merger = PdfFileMerger()
    for pdf in input_pdfs:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()
    logger.info(f"Merged PDF saved to {output_pdf}")

def convert_pdf_to_images(pdf_path, output_dir):
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"{i}_out.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)
    logger.info(f"Converted {pdf_path} to images.")
    return image_paths

def concatenate_images_vertically(image_paths, save_path):
    images = [Image.open(img_path) for img_path in image_paths]
    min_width = min(im.width for im in images)
    total_height = sum(im.height for im in images)
    concatenated_image = Image.new("RGB", (min_width, total_height))

    y_offset = 0
    for im in images:
        concatenated_image.paste(im, (0, y_offset))
        y_offset += im.height

    concatenated_image.save(save_path)
    logger.info(f"Concatenated image saved to {save_path}")

def upload_file_to_zendesk(ticket_id, file_path, message):
    upload_url = f"{ZENDESK_API_URL}/uploads.json?filename={os.path.basename(file_path)}"
    with open(file_path, 'rb') as file:
        response = requests.post(upload_url, auth=(ZENDESK_EMAIL, ZENDESK_TOKEN), files={'file': file})
    
    if response.status_code == 201:
        upload_token = response.json()['upload']['token']
        comment_url = f"{ZENDESK_API_URL}/tickets/{ticket_id}.json"
        data = {
            "ticket": {
                "comment": {
                    "body": message,
                    "uploads": [upload_token]
                }
            }
        }
        update_response = requests.put(comment_url, json=data, auth=(ZENDESK_EMAIL, ZENDESK_TOKEN))
        
        if update_response.status_code == 200:
            logger.info(f"File uploaded to ticket {ticket_id} successfully.")
        else:
            logger.error(f"Failed to update ticket {ticket_id}: {update_response.status_code} - {update_response.text}")
    else:
        logger.error(f"Failed to upload file: {response.status_code} - {response.text}")

def main():
    # Example SQL queries
    trend_query = "SELECT date, variableA FROM your_table WHERE name = 'ExampleName'"
    density_query = "SELECT x, y FROM your_table WHERE name = 'ExampleName'"

    # Query data
    df_trend = query_data(trend_query)
    df_density = query_data(density_query)

    # Generate charts
    output_dir = tempfile.mkdtemp()
    trend_pdf = os.path.join(output_dir, "trend_chart.pdf")
    density_pdf = os.path.join(output_dir, "density_plot.pdf")
    merged_pdf = os.path.join(output_dir, "merged_output.pdf")
    final_image = os.path.join(output_dir, "final_output.png")

    if df_trend is not None:
        create_trend_chart(df_trend, "variableA", trend_pdf)

    if df_density is not None:
        create_density_plot(df_density, density_pdf)

    append_pdfs([trend_pdf, density_pdf], merged_pdf)

    # Convert PDF to images and concatenate
    image_paths = convert_pdf_to_images(merged_pdf, output_dir)
    concatenate_images_vertically(image_paths, final_image)

    # Upload to ZenDesk
    ticket_id = 123456  # Example ticket ID
    message = "Please find the attached trend chart and density plot."
    upload_file_to_zendesk(ticket_id, final_image, message)

    # Clean up temporary files
    for path in [trend_pdf, density_pdf, merged_pdf] + image_paths:
        os.remove(path)
    logger.info("Temporary files cleaned up.")

if __name__ == "__main__":
    main()
