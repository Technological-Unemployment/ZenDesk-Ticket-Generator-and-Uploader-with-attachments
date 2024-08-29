import os
import tempfile
import datetime
import logging

import psycopg2 as pg
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches
from PyPDF2 import PdfFileMerger
from PIL import Image
from pdf2image import convert_from_path
from zenpy import Zenpy
from zenpy.lib.api_objects import Comment

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables for credentials
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_TOKEN = os.getenv("ZENDESK_TOKEN")
ZENDESK_SUBDOMAIN = os.getenv("ZENDESK_SUBDOMAIN")

# Database credentials
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Create Zenpy client
zenpy_client = Zenpy(email=ZENDESK_EMAIL, token=ZENDESK_TOKEN, subdomain=ZENDESK_SUBDOMAIN)


def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using environment variables.
    """
    return pg.connect(
        dbname=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def query_data(name, query_template):
    """
    Executes a query against the PostgreSQL database.

    Args:
        name (str): The name to filter the query on.
        query_template (str): The SQL query template to execute.

    Returns:
        pd.DataFrame: DataFrame with the query results.
    """
    try:
        with get_db_connection() as connection:
            query = query_template.format(name=name)
            df = pd.read_sql_query(query, con=connection)
        return df
    except (pg.DatabaseError, Exception) as error:
        logger.error(f"Error while querying the database: {error}")
        return None


def create_trend_chart(df, variable, save_path):
    """
    Creates and saves a trend chart as a PDF.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
        variable (str): The column name to plot.
        save_path (str): The path where the PDF will be saved.
    """
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(df['newdate'], df[variable], "o-")
    plt.grid(axis="y")
    plt.xticks(df['newdate'], rotation=0)
    plt.title(f"{df.iloc[0, 0]} - {variable} Chart", fontsize=16)
    plt.ylabel(f"Average {variable} per Event", fontsize=15)
    plt.axhline(y=df[variable].median(), linestyle='-.', color='orange', label='Median')
    plt.legend(loc="best", facecolor="white", frameon=True)
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Trend chart saved to {save_path}")


def create_density_plot(df, save_path):
    """
    Creates and saves a density plot as a PDF.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
        save_path (str): The path where the PDF will be saved.
    """
    with PdfPages(save_path) as pdf:
        sns.set_style("whitegrid")
        rect = patches.Rectangle(
            (-1, 1.5), 2, 2, linewidth=1, edgecolor="k", facecolor="none"
        )
        zone = sns.jointplot(
            x=df["side"],
            y=df["height"],
            kind="kde",
            color="red",
            shade_lowest=False,
        )
        zone.ax_joint.add_patch(rect)
        zone.ax_joint.set_xlim(-2, 2)
        zone.ax_joint.set_ylim(1, 4)
        plt.title(f"{df.iloc[0, 0]} - Density Plot Title - 2020", fontsize=10, loc="right")
        pdf.savefig()
        plt.close()
    logger.info(f"Density plot saved to {save_path}")


def append_pdfs(input_pdfs, output_pdf):
    """
    Merges multiple PDFs into a single PDF.

    Args:
        input_pdfs (list of str): List of file paths to the PDFs to merge.
        output_pdf (str): The file path for the merged PDF.
    """
    merger = PdfFileMerger()
    for pdf in input_pdfs:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()
    logger.info(f"PDFs merged into {output_pdf}")


def convert_pdf_to_png(pdf_path, output_dir):
    """
    Converts each page of a PDF to a separate PNG file.

    Args:
        pdf_path (str): The path to the PDF file.
        output_dir (str): The directory where PNG files will be saved.

    Returns:
        list of str: List of file paths to the generated PNG files.
    """
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"{i}_out.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)
    logger.info(f"Converted {pdf_path} to PNG images.")
    return image_paths


def concatenate_images_vertically(image_paths, save_path):
    """
    Concatenates multiple images vertically into a single image.

    Args:
        image_paths (list of str): List of file paths to the images to concatenate.
        save_path (str): The file path for the concatenated image.
    """
    images = [Image.open(img_path) for img_path in image_paths]
    min_width = min(im.width for im in images)
    resized_images = [
        im.resize((min_width, int(im.height * min_width / im.width)), resample=Image.BICUBIC)
        for im in images
    ]
    total_height = sum(im.height for im in resized_images)
    concatenated_image = Image.new("RGB", (min_width, total_height))

    y_offset = 0
    for im in resized_images:
        concatenated_image.paste(im, (0, y_offset))
        y_offset += im.height

    concatenated_image.save(save_path, "PNG")
    logger.info(f"Images concatenated and saved to {save_path}")


def upload_file_to_zendesk(ticket_id, file_path):
    """
    Uploads a file to a ZenDesk ticket.

    Args:
        ticket_id (int): The ID of the ZenDesk ticket.
        file_path (str): The path to the file to upload.
    """
    upload = zenpy_client.attachments.upload(file_path)
    ticket = zenpy_client.tickets(id=ticket_id)
    ticket.comment = Comment(
        body="Uploaded Trend Charts and Density Plots",
        public=False,
        uploads=[upload.token],
    )
    zenpy_client.tickets.update(ticket)
    logger.info(f"Uploaded {file_path} to ZenDesk ticket {ticket_id}")


def main():
    # Read reference sheet
    ref = pd.read_csv(r"C:\\ComputerName\\ReferenceSheet.csv")

    # Define date range (last 365 days)
    date_range = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(365)]

    # Search for ZenDesk tickets
    for ticket in zenpy_client.search(
        created_between=[date_range[-1], date_range[0]],
        group="Data Analytics",
        type="ticket",
        status=['new', 'open'],
        minus='negated'
    ):
        logger.info(f"Processing ticket {ticket.id}")
        forName = str(ticket.custom_fields[5])
        Name = forName[27: len(forName) - 2]

        SQLnameOG = ref.loc[ref.iloc[:, 1] == Name, ref.columns[0]].values[0]
        name = f"'{SQLnameOG}'"
        SQLname = SQLnameOG.replace(" ", "").replace("-", "")

        output_dir = os.path.join("C:\\Name_of_Folder")
        trend_pdf = os.path.join(output_dir, f"{SQLname}T.pdf")
        density_pdf = os.path.join(output_dir, f"{SQLname}D.pdf")
        merged_pdf = os.path.join(output_dir, f"{SQLname}.pdf")

        # Qsearch TChart
        df_trend = query_data(name, "YOUR TREND SQL QUERY HERE")
        if df_trend is not None:
            df_trend.fillna(0, inplace=True)
            create_trend_chart(df_trend.tail(30), 'variableA', trend_pdf)

        # Qsearch Density plots
        df_density = query_data(name, "YOUR DENSITY SQL QUERY HERE")
        if df_density is not None:
            df_density.fillna(0, inplace=True)
            create_density_plot(df_density, density_pdf)

        # Merge PDFs
        append_pdfs([trend_pdf, density_pdf], merged_pdf)

        # Convert merged PDF to PNGs
        image_paths = convert_pdf_to_png(merged_pdf, output_dir)

        # Concatenate images
        final_image_path = os.path.join(output_dir, f"{SQLname}out.png")
        concatenate_images_vertically(image_paths, final_image_path)

        # Clean up intermediate files
        for file_path in [trend_pdf, density_pdf, merged_pdf] + image_paths:
            os.remove(file_path)

        # Upload to ZenDesk
        upload_file_to_zendesk(ticket.id, final_image_path)

if __name__ == "__main__":
    main()
