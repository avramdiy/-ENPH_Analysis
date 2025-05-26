from flask import Flask, render_template_string, Response
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Path to the file
FILE_PATH = r"C:\Users\avram\OneDrive\Desktop\TRG Week 25\enph.us.txt"

@app.route('/')
def display_table():
    # Check if the file exists
    if not os.path.exists(FILE_PATH):
        return "File not found. Please check the file path.", 404

    # Load the file into a Pandas DataFrame
    try:
        # Auto-detect delimiter
        with open(FILE_PATH, 'r') as file:
            sample = file.read(1024)
            detected_delimiter = csv.Sniffer().sniff(sample).delimiter
        
        # Load the DataFrame using the detected delimiter
        df = pd.read_csv(FILE_PATH, delimiter=detected_delimiter)
        
        # Ensure the date column exists
        if 'Date' not in df.columns:
            return "The file does not contain a 'Date' column.", 400

        # Convert the 'Date' column to datetime
        try:
            df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        except ValueError as e:
            return f"Error parsing 'Date' column: {str(e)}", 400

        # Filter rows based on the specified date range
        start_date = pd.to_datetime('2013-01-01')  # Start date in datetime format
        end_date = pd.to_datetime('2016-12-31')    # End date in datetime format
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        # Reorder date to 'MM-DD-YYYY' format
        df['Date'] = df['Date'].dt.strftime('%m-%d-%Y')

        # Drop the 'OpenInt' column if it exists
        if 'OpenInt' in df.columns:
            df = df.drop(columns=['OpenInt'])

        # Check if any data remains after filtering
        if df.empty:
            return "No data available for the specified date range.", 400

    except Exception as e:
        return f"Error processing the file: {str(e)}", 500

    # Convert DataFrame to HTML
    html_table = df.to_html(classes='table table-striped', index=False)

    # Render the HTML table
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <title>Filtered Data Table</title>
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center">Filtered Data Table</h1>
            {html_table}
        </div>
    </body>
    </html>
    """
    return render_template_string(template)

@app.route('/quarterly')
def plot_quarterly_open():
    if not os.path.exists(FILE_PATH):
        return "File not found. Please check the file path.", 404

    try:
        with open(FILE_PATH, 'r') as file:
            sample = file.read(1024)
            detected_delimiter = csv.Sniffer().sniff(sample).delimiter
        
        df = pd.read_csv(FILE_PATH, delimiter=detected_delimiter)

        if 'Date' not in df.columns or 'Open' not in df.columns:
            return "The file does not contain the required columns.", 400

        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        df = df[(df['Date'] >= '2013-01-01') & (df['Date'] <= '2016-12-31')]

        # Resample to quarterly average "Open" price
        df.set_index('Date', inplace=True)
        quarterly_open = df['Open'].resample('Q').mean()
        quarterly_low = df['Low'].resample('Q').mean()
        quarterly_high = df['High'].resample('Q').mean()

        # Plot the data
        plt.figure(figsize=(10, 6))
        quarterly_open.plot(kind='line', marker='o', color='blue')
        quarterly_low.plot(kind='line', marker='o', color='red')
        quarterly_high.plot(kind='line', marker='o', color='green')
        plt.title("Quarterly Average Prices (2013-2016)")
        plt.xlabel("Quarter")
        plt.ylabel("Average Prices")
        plt.grid(True)
        plt.legend(loc='upper right')
        plt.tight_layout()

        # Save the plot to a BytesIO buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        return Response(buf, mimetype='image/png')

    except Exception as e:
        return f"Error processing the file: {str(e)}", 500    

if __name__ == '__main__':
    # Check for file existence before running the app
    if not os.path.exists(FILE_PATH):
        print(f"Error: File at {FILE_PATH} does not exist. Please check the file path.")
    else:
        app.run(debug=True)
