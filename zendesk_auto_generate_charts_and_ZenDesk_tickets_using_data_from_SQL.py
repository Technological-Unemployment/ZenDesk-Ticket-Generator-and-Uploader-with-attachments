import psycopg2 as pg
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as datef
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as patches
import seaborn as sns
from PyPDF2 import PdfFileMerger
from zenpy.lib.api_objects import Comment
from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError,
)
import os
import tempfile
from PIL import Image
import datetime
from zenpy import Zenpy
import numpy as np

def pdfAppend(str6, str7, str8):
    pdfs = [str6, str7]
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(pdf)

    merger.write(str8)
    merger.close()


def QsearchT(name):
    # Qsearch TChart
    try:
        connection = pg.connect(
            dbname="your_dbname",
            host="your_host",
            port="5439",
            user="username",
            password="password",
        )
        query = f"""Add your SQL Query to automatically generate trend charts by name;
                    WHERE name = '{name}'"""
        df = pd.read_sql_query(query, con=connection)
        connection.close() 
        return df
    except (Exception, pg.DatabaseError) as error:
        print("Error while connecting to PostgreSQL database: ", error)
        return None


def QsearchD(name):
    try:
        connection = pg.connect(
             dbname="your_dbname",
            host="your_host",
            port="5439",
            user="username",
            password="password",
        )
        query = f"""Add your SQL Query to automatically generate density charts by name;
                    WHERE name = '{name}'"""
        df2 = pd.read_sql_query(query, con=connection)
        connection.close()
        return df2
    except (Exception, pg.DatabaseError) as error:
        print("Error while connecting to PostgreSQL database: ", error)
        return None
    
    
def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [
        im.resize((min_width, int(im.height * min_width/ im.width)), resample=resample)
        for im in im_list
    ]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new("RGB", (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst


import pandas as pd
import datetime
from matplotlib.backends.backend_pdf import PdfPages
from zenpy import Zenpy

# Read reference sheet
ref = pd.read_csv(r"C:\\ComputerName\\ReferenceSheet.csv")

# ZenDesk credentials
creds1 = {
    "email": "your_email",
    "token": "your_ZenDesk_token",
    "subdomain": "your_customer_name_from_ZenDesk",
}

# Create Zenpy client
zenpy_client = Zenpy(**creds1)

# Define date range
def update_date_format(n):
    now = datetime.datetime.now()
    date_range = []
    for i in range(n):
        d = now - datetime.timedelta(days=i)
        date_range.append(d.strftime('%Y-%m-%d'))
    return date_range

date_range = update_date_format(365)

# Search for tickets
for ticket in zenpy_client.search(
    created_between=[date_range[-1], date_range[0]],
    group="Data Analytics",
    type="ticket",
    status=['new', 'open'],
    minus='negated'
):
    print(ticket)
    print(ticket.custom_fields[5])
    # using custom field 5 to find SQL name for each generated ticket location
    forName = str(ticket.custom_fields[5])
    Name = forName[27 : len(forName) - 2]
    for i in range(len(ref)):
        if Name == ref.iloc[i, 1]:
            SQLnameOG = str(ref.iloc[i, 0])
            name = "'" + SQLnameOG + "'"
            SQLname = SQLnameOG.replace(" ", "")
            SQLname = SQLname.replace("-", "")
            print(SQLname)
            print(" ")
            str1 = "C:\\Name_of_Folder\\"
            str2 = SQLname + "T"
            str4 = SQLname + "D"
            str5 = SQLname
            str3 = ".pdf"

            # Qsearch TChart and creation
            df = QsearchT(name)
            df.fillna(0, inplace=True)

            Last30 = df.tail(30)
            datelist = []

                    fig, ax = plt.subplots(figsize=(13, 5))
                    a = np.nanmax(df.variableB); b = np.nanmax(df.variableC)
                    c = max(a,b) + 2.0
                    d = np.nanmax(df.variableA) + 2.0
                    
                    if x == 'variableA':
                       plt.ylim(0, d)    
                    if x == 'variableB' or x == 'variableC':
                       plt.ylim(0, c)
                    if x == 'zs':
                       plt.ylim(-1.0, 1)

                    ax.plot(Last30.newdate, Last30[x], "o-")
                    plt.grid(axis="y")
                    plt.xticks(Last30.newdate, rotation=0)
                    plt.gca().margins(x=0)
                    plt.gcf().canvas.draw()
                    tl = plt.gca().get_xticklabels()
                    maxsize = max([t.get_window_extent().width for t in tl])
                    m = 0.5  # inch margin
                    s = maxsize / plt.gcf().dpi * (len(Last30.index)) + 2 * m
                    margin = m / plt.gcf().get_size_inches()[0]

                    plt.gcf().subplots_adjust(left=margin, right= 1.0 -margin) #
                    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])
                    
                    if x == 'variableB' or x == 'variableC' or x == 'variableA':
                       plt.axhline(y=median, linestyle='-.', color='orange', label='median')
                    else:
                       plt.axhline(y=mean, linestyle='--', color='g', label='mean')
                       

                    plt.axhline(y=USL, color="k", label="USL")

                    if LSL == "empty":
                        LSL = "skip"
                    else:
                        plt.axhline(y=LSL, color="k", label="LSL")
                    plt.suptitle(str(Last30.iloc[0, 0]) + " - " + x + " Chart",fontsize=16,)
                    plt.ylabel("Average " + x + " per Event", fontsize=15)
                    plt.legend(loc="best", facecolor="white", frameon=True)
                    pdf.savefig()
                    plt.close()

            # Qsearch Density plots and creation
            df2 = QsearchD(name)
            df2.fillna(0, inplace=True)
            with PdfPages(r"C:\\Name_of_Folder\\" + str4 + str3, "r") as pdf:
                CalledK = df2.loc[df2["feature"] == "Another name of feature"]
                sns.set_style("whitegrid")
                rect = patches.Rectangle(
                    (-1, 1.5), 2, 2, linewidth=1, edgecolor="k", facecolor="none"
                )
                zone = sns.jointplot(
                    x=CalledK["side"],
                    y=CalledK["height"],
                    kind="kde",
                    color="red",
                    shade_lowest=False,
                )
                zone.ax_joint.add_patch(rect)
                zone.ax_joint.set_xlim(-2, 2)
                zone.ax_joint.set_ylim(1, 4)
                plt.title(str(df2.iloc[0, 0]) + " - " +"Density Plot Title - 2020\n\n\n\n",fontsize=10,loc="right",)
                pdf.savefig()
                plt.close()

            # Automating the filepaths
            str6 = str1 + str2 + str3

            str7 = str1 + str4 + str3

            str8 = str1 + str5 + str3
            pdfAppend(str6, str7, str8)

            # Pdf to PNG (Each page to separate PNG)
            filename = str8
            images = convert_from_path(filename)

            temp_list = []
            for i, image in enumerate(images):
                fP = str1 + str2 + str(i) + "out.png"
                image.save(fP, "PNG")
                temp_list.append(r"C:\\Name_of_Folder\\" + str2 + str(i) + "out.png")

            # Concatenate all PNG files to one
            im0 = Image.open(temp_list[0])
            im1 = Image.open(temp_list[1])
            im2 = Image.open(temp_list[2])
            im3 = Image.open(temp_list[3])
            im4 = Image.open(temp_list[4])
            im5 = Image.open(temp_list[5])
            im6 = Image.open(temp_list[6])
            im7 = Image.open(temp_list[7])
            im8 = Image.open(temp_list[8])
            im9 = Image.open(temp_list[9])
            im10 = Image.open(temp_list[10])

            fP = str1 + str5 + "out.png"
            get_concat_v_multi_resize([im0, im1, im2, im3, im4, im5, im6, im7, im8, im9, im10]).save(fP, "PNG")

            # Extra PDF and PNG deletion
            for i in range(0, 10):
                os.remove(temp_list[i])

            os.remove(str6)
            os.remove(str7)
            os.remove(str8)

            # Upload to Zenpy Ticket
            tname = str5 + "out.png"
            upload_comb = zenpy_client.attachments.upload(
                "C:/Quality/" + str5 + "out.png"
            )
            ticket = zenpy_client.tickets(id=ticket.id)
            ticket.comment = Comment(
                body="Uploaded Trend Charts and Density Plots",
                public=False,
                uploads=[upload_comb.token],
            )
            zenpy_client.tickets.update(ticket)
            break
