#Import libraries and modules
from fastapi import FastAPI
import pandas as pd
import numpy as np
import requests
from io import BytesIO
from fastapi import FastAPI, HTTPException, Query

#Create an instance of FAST API 
app = FastAPI()

#URL of the Excel file from the GitHub repository
EXCEL_URL = "https://raw.githubusercontent.com/yaswanth-iitkgp/IRIS_Public_Assignment/main/Data/capbudg.xls"  

#Function to send request to extract Excel file URL
def extract_excel_file():
    """
    Returns:
    File's content as a byte's object 
    """
    response = requests.get(EXCEL_URL)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unable to retrieve the Excel file")
    return BytesIO(response.content)

#Function to return normalized text string 
def normalize(text: str) -> str:
    """Removes whitespaces, before converting into uppercase chracters 
    and again removes trailing '=' symbol
    
    Returns:
    text (str): Normalied text
    """
    return text.strip().upper().rstrip('=')

#Function to search header row of table in sheet of Excel file 
def locate_table_header(table_name: str):
    """
    Parameters:
    table_name (str): Name of table
    
    Returns:
    tuple: Returns (sheet_name, header_index, table_col, df)
    
    where:
      header_index: row index of the header within the DataFrame df,
      table_col: column index of the found table name

    If table is not found in any sheet, then it raises an HTTP 404 error
    """
    excel_file = pd.ExcelFile(extract_excel_file())
    table_name_norm = normalize(table_name)
     
    for sheet in excel_file.sheet_names:
        #Reset file pointer for each sheet
        file_content = extract_excel_file()
        df = pd.read_excel(file_content, sheet_name=sheet, header=None)
        for i, row in df.iterrows():
            #Skip empty rows
            if pd.isna(row.iloc[0]) or (isinstance(row.iloc[0], str) and row.iloc[0].strip() == ""):
                continue
            table_col = None
            #Check first column
            if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], str):
                if normalize(row.iloc[0]) == table_name_norm:
                    table_col = 0
            #Check the 5th column if it exists
            if table_col is None and len(row) > 4 and pd.notna(row.iloc[4]) and isinstance(row.iloc[4], str):
                if normalize(row.iloc[4]) == table_name_norm:
                    table_col = 4
            #Search the entire row
            if table_col is None:
                for j, cell in enumerate(row):
                    if pd.notna(cell) and isinstance(cell, str):
                        if normalize(cell) == table_name_norm:
                            table_col = j
                            break
            if table_col is not None:
                return sheet, i, table_col, df
    raise HTTPException(status_code=404, detail=f"Table '{table_name}' doesn't exist")

    
#Function to extract table names from the sheet
def extract_table_names() -> list:
    """
    Searches the table by identifying header values in uppercase from corresponding columns and returns table names as a list
    
    Returns:
    list: Table names (str)
    """
    
    #Downloads the Excel file by sending request
    response = requests.get(EXCEL_URL)
    if response.status_code != 200:
        return []  
    file_content = BytesIO(response.content)
    
    #Read Excel file
    excel_file = pd.ExcelFile(file_content)
    retrieved_tables = []  
    
    #Loop through each sheet in the workbook
    for sheet_name in excel_file.sheet_names:
        # Reset pointer so the file can be re-read for each sheet
        file_content.seek(0)
        df = pd.read_excel(file_content, sheet_name=sheet_name, header=None)
        #Checks if it's inside a table 
        in_table = False 
        
        #Iterate over rows of the created dataframe
        for idx, row in df.iterrows():
            #Checks if the row is empty
            #The row would be empty if its first cell contains either NaN or a blank string 
            first_cell = row.iloc[0]
            is_empty_row = pd.isna(first_cell) or (isinstance(first_cell, str) and first_cell.strip() == "")
            
            if is_empty_row:
                #An empty row indicates table block has ended
                in_table = False
                continue
            
            #If not inside a table, then this cell is a header row
            #Either this is the first row or followed next by an empty row
            if not in_table:
                #All cells are extracted from this row that are strings, and if they are fully uppercase, we consider them table names.
                for cell in row:
                    if pd.notna(cell) and isinstance(cell, str):
                        cell = cell.strip()
                        if cell and cell.isupper():
                            #Appends only if not already retrieved
                            if cell not in retrieved_tables:
                                retrieved_tables.append(cell)
                #Checks if the cell is inside a table block
                in_table = True
        
    return retrieved_tables

#Function to extract row names from table 
def extract_table_data(table_name: str) -> dict:
    """
    When the header row of the table is detected, target column extracts the corresponding row names below it
    
    Parameters:
    table_name (str): Name of table
    
    Returns:
    data_list:Returning a dictionary with table name as key and a list of row names as value
    """
    
    #Follows same logic as locate_table_header function for searching header rows
    
    response = requests.get(EXCEL_URL)
    if response.status_code != 200:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve the Excel file"
        )
    file_content = BytesIO(response.content)
    excel_file = pd.ExcelFile(file_content)
    table_found = False
    data_list = []
    target_col = None
    header_index = None

    #Iterates through every sheet
    for sheet_name in excel_file.sheet_names:
        file_content.seek(0)
        df = pd.read_excel(file_content, sheet_name=sheet_name, header=None)
        in_table = False

        #Looks for the header row using candidate search (1st column, 4th column and then full row)
        for i, row in df.iterrows():
            #Skips empty rows by checking the first cell
            first_cell = row.iloc[0] if len(row) > 0 else None
            if pd.isna(first_cell) or (isinstance(first_cell, str) and first_cell.strip() == ""):
                in_table = False
                continue

            target = None
            col_index = None
            #Checks 1st column
            if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], str):
                val = row.iloc[0].strip()
                if val.upper() == table_name.upper():
                    target = val
                    col_index = 0
            #Checks 5th column
            if target is None and len(row) > 4:
                if pd.notna(row.iloc[4]) and isinstance(row.iloc[4], str):
                    val = row.iloc[4].strip()
                    if val.upper() == table_name.upper():
                        target = val
                        col_index = 4
            #Checks entire row
            if target is None:
                for j, cell in enumerate(row):
                    if pd.notna(cell) and isinstance(cell, str):
                        val = cell.strip()
                        if val.upper() == table_name.upper():
                            target = val
                            col_index = j
                            break

            if target is not None:
                in_table = True
                target_col = col_index
                header_index = i
                table_found = True
                break  

        if table_found:
            #Retrieve starting row index for data extraction
            start_index = header_index + 1
            if start_index < len(df):
                #Adjusts start index when the table cell next to header is empty
                next_row = df.iloc[start_index]
                if target_col >= len(next_row) or pd.isna(next_row[target_col]) or \
                   (isinstance(next_row[target_col], str) and next_row[target_col].strip() == ""):
                    start_index = header_index + 2

            #Iterate over rows beignning from the adjusted start_index
            for k in range(start_index, len(df)):
                current_row = df.iloc[k]
                #If the table cell for the current row is empty, then it's assumed there's not any table data
                if target_col >= len(current_row) or pd.isna(current_row[target_col]) or \
                   (isinstance(current_row[target_col], str) and current_row[target_col].strip() == ""):
                    break
                data_list.append(str(current_row[target_col]).strip())
            break  

    if not table_found:
        raise HTTPException(
            status_code=404, detail=f"Table '{table_name}' doesn't exist"
        )
    return {table_name: data_list}

#Function to return the sum of numerical values for the selected row
def extract_row_num(table_name: str, row_name: str) -> dict:     
    """
    Searches the provided table name and row name to perform additon of all numbers in the corresponding column cells
    
    Parameters:
    table_name (str): Name of table
    row_name (str): Name of row
    
    Returns:
    sum (int): Addition of all numeric values in the selected row
    """
    
    # Locate the table header via the helper function.
    sheet_found, header_index, target_col, df = locate_table_header(table_name)
    target_row_name = normalize(row_name)
    
    #Iterate over rows next to the header row
    for idx in range(header_index + 1, len(df)):
        current_row = df.iloc[idx]
        #If the target column cell is empty, then it is assumed to be end of table block
        if target_col >= len(current_row) or pd.isna(current_row[target_col]) or \
           (isinstance(current_row[target_col], str) and current_row[target_col].strip() == ""):
            break
        
        cell_val = ""
        if pd.notna(current_row[target_col]) and isinstance(current_row[target_col], str):
            cell_val = normalize(current_row[target_col])
        
        if cell_val == target_row_name:
            #Looks for the value from the next column to extract and skips to two columns if it's empty
            next_col_index = target_col + 1
            two_cols_away_index = target_col + 2
            
            next_value = (
                str(current_row[next_col_index]).strip() if next_col_index < len(current_row) and pd.notna(current_row[next_col_index])
                else ""
            )
            two_cols_away_value = (
                str(current_row[two_cols_away_index]).strip() if two_cols_away_index < len(current_row) and pd.notna(current_row[two_cols_away_index])
                else ""
            )
            
            found_value = next_value if next_value else two_cols_away_value
            
            #If value ends with '%', then the '%' sign is removed
            if found_value.endswith('%'):
                found_value = found_value.rstrip('%').strip()
            else:
                #Multiply by 100 to convert the numeric value from decimal to percent
                try:
                    num_val = float(found_value)
                    #If number is less than or eqaual to 1, then it represents percentage value
                    if num_val <= 1:
                        num_val *= 100
                    #Removes decimal digits of number when it has an integer value
                    if num_val.is_integer():
                        found_value = str(int(num_val))
                    else:
                        found_value = str(num_val)
                except ValueError:
                    pass
            
            if found_value:
                return {
                    "table name": table_name,
                    "row name": row_name,
                    "sum": int(found_value)
                }
            break

    raise HTTPException(status_code=404, detail=f"Row name '{row_name}' not found or no valid sum in table '{table_name}'")

@app.get("/list_tables")
def list_tables():
    names = extract_table_names()
    return {"tables_list": names}

@app.get("/get_table_details")
def table_data(table_name: str = Query(..., description="Name of the table to extract data for")):
    result = extract_table_data(table_name)
    return result

@app.get("/row_sum")
def row_num(
    table_name: str = Query(..., description="Name of the table"),
    row_name: str = Query(..., description="Name of the row")
):
    result = extract_row_num(table_name, row_name)
    return result
