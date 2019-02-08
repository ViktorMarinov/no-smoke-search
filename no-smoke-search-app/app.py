from flask import Flask, url_for, render_template
from flask import flash, render_template, request, redirect
from model.inverse_index import parse_query, find_matches
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/results')
def search_results():
    search_query = request.args.get('search_query')

    parsed_query = parse_query(search_query)
    results = find_matches(parsed_query)

    items = rows_to_items(results)

    for result in rows_to_items(results):
        print(result)

    return render_template('results.html', search=search_query, items=items)


def rows_to_items(results):
    items = [row[1]for row in results.iterrows()]
    for item in items:
        item.tokens = set([t for t in item.tokens if len(t) > 1])
    return items


if __name__ == '__main__':
    app.run()
