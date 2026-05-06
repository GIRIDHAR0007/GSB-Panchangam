from flask import Flask, render_template, request
from datetime import datetime, date
import panchangam

app = Flask(__name__)

DEFAULT_LATITUDE = 8.5241
DEFAULT_LONGITUDE = 76.9366

@app.route('/', methods=['GET', 'POST'])
def home():
    selected_date = date.today()
    if request.method == 'POST':
        user_date = request.form.get('date')
        if user_date:
            try:
                selected_date = datetime.strptime(user_date, '%Y-%m-%d').date()
            except ValueError:
                selected_date = date.today()

    data = panchangam.get_panchangam_for_date(
        selected_date,
        latitude=DEFAULT_LATITUDE,
        longitude=DEFAULT_LONGITUDE,
    )

    return render_template(
        'index.html',
        data=data,
        selected_date=selected_date.isoformat(),
    )

if __name__ == '__main__':
    app.run(debug=True)