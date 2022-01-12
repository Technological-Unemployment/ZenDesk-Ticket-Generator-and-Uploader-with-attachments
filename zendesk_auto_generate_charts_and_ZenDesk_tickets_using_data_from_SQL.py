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
    connection = pg.connect(
        dbname="your_dbname",
        host="your_host",
        port="5439",
        user="username",
        password="password",
    )
    df = pd.read_sql_query(
        """Add your SQL Query with f string command to automatically generate trend charts by name;
    """, con=connection)
    connection.close() 
    return df
    

def QsearchD(name):
    connection = pg.connect(
         dbname="your_dbname",
        host="your_host",
        port="5439",
        user="username",
        password="password",
    )
    df2 = pd.read_sql_query(
        """Add your SQL Query with f string command to automatically generate density charts by name;
    """,con=connection)
    connection.close()
    return df2
    
    
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


# Read in reference sheet if your customer names aren't identical in ZenDesk as in your SQL database
ref = pd.read_csv(r"C:\\ComputerName\\ReferenceSheet.csv")

creds1 = {
    "email": "your_email",
    "token": "your_ZenDesk_token",
    "subdomain": "your_customer_name_from_ZenDesk",
}


zenpy_client = Zenpy(**creds1)

yesterday = datetime.datetime.now() - datetime.timedelta(days=62)
yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0) # Returns a copy
today = datetime.datetime.now()
today = today.replace(hour=23, minute=59, second=0, microsecond=0) # Returns a copy
for ticket in zenpy_client.search(
    created_between=[yesterday, today],
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
            
            
            ## If your date format needs to be restructured for it print nicely on your charts
            with PdfPages(r"C:\\Name_of_Folder\\" + str2 + str3, "r") as pdf:
                for i in Last30["date1"]:
                    elif i[4:6] == "01" and i[0:4] == "2020":
                        update = i.replace("202001", "2020 \n Jan-")
                        datelist.append(update)
                    elif i[4:6] == "02" and i[0:4] == "2020":
                        update = i.replace("202002", "2020 \n Feb-")
                        datelist.append(update)
                    elif i[4:6] == "03" and i[0:4] == "2020":
                        update = i.replace("202003", "2020 \n Mar-")
                        datelist.append(update)
                    elif i[4:6] == "04" and i[0:4] == "2020":
                        update = i.replace("202004", "2020 \n Apr-")
                        datelist.append(update)
                    elif i[4:6] == "05" and i[0:4] == "2020":
                        update = i.replace("202005", "2020 \n May-")
                        datelist.append(update)
                    elif i[4:6] == "06" and i[0:4] == "2020":
                        update = i.replace("202006", "2020 \n Jun-")
                        datelist.append(update)
                    elif i[4:6] == "07" and i[0:4] == "2020":
                        update = i.replace("202007", "2020 \n Jul-")
                        datelist.append(update)
                    elif i[4:6] == "08" and i[0:4] == "2020":
                        update = i.replace("202008", "2020 \n Aug-")
                        datelist.append(update)
                    elif i[4:6] == "09" and i[0:4] == "2020":
                        update = i.replace("202009", "2020 \n Sep-")
                        datelist.append(update)
                    elif i[4:6] == "10" and i[0:4] == "2020":
                        update = i.replace("202010", "2020 \n Oct-")
                        datelist.append(update)
                    elif i[4:6] == "11" and i[0:4] == "2020":
                        update = i.replace("202011", "2020 \n Nov-")
                        datelist.append(update)
                    elif i[4:6] == "12" and i[0:4] == "2020":
                        update = i.replace("202012", "2020 \n Dec-")
                        datelist.append(update)
                    else:
                        update = i
                        datelist.append(update)

                Last30.loc[:, "newdate"] = datelist
                #Last30['newdate'] = pd.Series(datelist, index=Last30.index)
                for x in Last30.columns[4:-1]:
                    SD = Last30[x].std()
                    mean = Last30[x].mean()
                    median = Last30[x].median()

                    if x == 'variableA':
                       USL = 7.0
                       LSL = 'empty'
                    elif x == 'variableB':
                      USL = 5.9
                      LSL = 'empty'
                    elif x == 'height':
                      USL = 5.9
                      LSL = 'empty'
                    elif x == 'side':
                      USL = 5.9
                      LSL = 'empty'
                    elif x == 'variableC' or 'variableD':
                       USL = 1
                       LSL = 0
                    else:
                       USL = 1
                       LSL = -1

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
