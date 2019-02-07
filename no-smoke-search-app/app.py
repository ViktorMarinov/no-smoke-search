from flask import Flask, url_for, render_template
from flask import flash, render_template, request, redirect

app = Flask(__name__)

# url_for('static', filename='style.css')

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/results')
def search_results():
    search_query = request.args.get('search_query')

    results = [1,2,3,5]
    return render_template('results.html', search=search_query, results=results)

if __name__ == '__main__':
    app.run()



        # results = search_string
        # if not results:
        #     flash('No results found!')
        #     return redirect('/')
        # else:
        #     # display results
