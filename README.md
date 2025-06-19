# FastAPI Excel Processor Assignment

### Potential improvements

Instead of FAST API, a possible alternative could be experimenting with Streamlit to build an interactive web application using a Python script, as it is convenient for someone who has limited experience with API development. It doesn't require making any API requests with the extra functionalities or methods such as 'GET', 'POST', 'PUT', etc. Also, it offers various pre-built components to create a user interface and form, requiring few lines of code. The application code works for older Excel files in xls format as it retrieves contents by sending requests to the file URL from the GitHub repository. The Python script can be written further to deal with the default file format, such as xlsx, to extend the assignment should the need arise. Last but not least, the addition operation can also be performed for some tables containing multiple values in different columns until the end of the block for the same row name.


### Missed Edge Cases

Apparently, this code wouldn't run and throw an error if in case the Excel file is empty, which is highly unlikely. In the application code, a couple of endpoints don't provide the exact intended JSON output for some cases. The 1st endpoint list_tables, fails to extract the name of the table 'BOOK VALUE & DEPRECIATION' since in the header row it appears distorted and not of standard type, unlike other tables. On the other hand, the row_sum endpoint only returns the numerical value from the next corresponding column if a selected table and row name contains numbers in more than 1 column cell. Instead, the 'sum' key in the structure of the JSON response would be equal to this value. This issue can be detected by inputting the table name 'OPERATING CASHFLOWS' and any of the row names by testing the endpoint using the POSTMAN app. Other than these scenarios, the code would run normally based on the assumption that tables exist along with their numeric records and would return JSON responses based on the input query parameters. 

### Testing

First go to in a terminal window and change the file path to the directory of the FAST API application file 'main.py'. 
```
cd [directory of app file]
```

Then, run the app with the following command : 
```
uvicorn main:app --host localhost --port 9090 --reload
```

The following URLS for the 3 endpoints can be tested for checking ouputs:

*   **Base URL:**

`http://localhost:9090`

*   **Endpoints URL:**

`http://localhost:9090/list_tables`

`http://localhost:9090/get_table_details`

`http://localhost:9090/row_sum`

*   **Postman Collection:** 
```json
{
	"info": {
		"_postman_id": "0c355279-5a84-482c-91c5-4a291222afed",
		"name": "FAST API",
		"schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
		"_exporter_id": "16657179"
	},
	"item": [
		{
			"name": "Tables List",
			"protocolProfileBehavior": {
				"disableBodyPruning": true
			},
			"request": {
				"auth": {
					"type": "noauth"
				},
				"method": "GET",
				"header": [],
				"body": {
					"mode": "formdata",
					"formdata": [
						{
							"key": "table_list",
							"value": "INITIAL INVESTMENT",
							"type": "text",
							"disabled": true
						}
					]
				},
				"url": {
					"raw": "http://localhost:9090/list_tables",
					"protocol": "http",
					"host": [
						"localhost"
					],
					"port": "9090",
					"path": [
						"list_tables"
					]
				}
			},
			"response": []
		},
		{
			"name": "Table Row Names",
			"protocolProfileBehavior": {
				"disableBodyPruning": true
			},
			"request": {
				"auth": {
					"type": "noauth"
				},
				"method": "GET",
				"header": [],
				"body": {
					"mode": "formdata",
					"formdata": [
						{
							"key": "",
							"value": "",
							"type": "text",
							"disabled": true
						}
					]
				},
				"url": {
					"raw": "http://localhost:9090/get_table_details?table_name=INITIAL INVESTMENT",
					"protocol": "http",
					"host": [
						"localhost"
					],
					"port": "9090",
					"path": [
						"get_table_details"
					],
					"query": [
						{
							"key": "table_name",
							"value": "INITIAL INVESTMENT"
						}
					]
				}
			},
			"response": []
		},
		{
			"name": "Table Row Sum",
			"request": {
				"auth": {
					"type": "noauth"
				},
				"method": "GET",
				"header": [],
				"url": {
					"raw": "http://localhost:9090/row_sum?table_name=INITIAL INVESTMENT&row_name=Initial Investment=",
					"protocol": "http",
					"host": [
						"localhost"
					],
					"port": "9090",
					"path": [
						"row_sum"
					],
					"query": [
						{
							"key": "table_name",
							"value": "INITIAL INVESTMENT"
						},
						{
							"key": "row_name",
							"value": "Initial Investment="
						}
					]
				}
			},
			"response": []
		}
	]
}
```
