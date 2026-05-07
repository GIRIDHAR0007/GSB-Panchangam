import sys
import os
from datetime import datetime, date
from flask import Flask, render_template, request

# Add parent directory to path to import panchangam
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import panchangam

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'))

DEFAULT_LATITUDE = 8.5241
DEFAULT_LONGITUDE = 76.9366

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_date = date.today()
    data = None
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        if date_str:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date_str = request.args.get('date')
        if date_str:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    try:
        data = panchangam.get_panchangam_for_date(
            selected_date,
            latitude=DEFAULT_LATITUDE,
            longitude=DEFAULT_LONGITUDE,
        )
    except Exception as e:
        print(f"Error fetching panchangam: {e}")
        data = None
    
    return render_template('index.html', selected_date=selected_date.strftime('%Y-%m-%d'), data=data)
