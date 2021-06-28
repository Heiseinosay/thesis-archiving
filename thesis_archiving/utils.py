import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz

def export_to_excel(file_prefix, data, columns):

    # https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#writing-excel-files-to-memory

    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html#

    # binary object
    output = BytesIO()

    # excel writer
    writer = pd.ExcelWriter(output, engine="openpyxl")

    df = pd.DataFrame(data, columns=columns)

    # write data to binary object
    df.to_excel(writer, index=False)
    writer.save()

    # seek pointer to beginning of the object to return the whole content
    output.seek(0)
    
    # file name
    date = datetime.now(tz=pytz.timezone('Asia/Manila')).strftime("%Y-%m-%d")
    download_name = file_prefix + date + ".xlsx"

    return output, download_name