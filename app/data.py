from flask import Flask, render_template_string
import pandas as pd
import os

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
        # Adjust delimiter based on your file structure (e.g., '\t' for tab-separated)
        df = pd.read_csv(FILE_PATH, delimiter="\t")
    except Exception as e:
        return f"Error reading the file: {str(e)}", 500
    
    # Convert DataFrame to HTML
    html_table = df.to_html(classes='table table-striped', index=False)
    
    # Render the HTML table
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <title>Data Table</title>
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center">Data Table</h1>
            {html_table}
        </div>
    </body>
    </html>
    """
    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True)
