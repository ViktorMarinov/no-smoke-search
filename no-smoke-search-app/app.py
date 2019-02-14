from flask import Flask, url_for, render_template
from flask import flash, render_template, request, redirect
from model.inverse_index import parse_query, find_matches
from model.duplicates import find_similar, find_similar_2
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', max_n_reports=10)

@app.route('/results')
def search_results():
    search_query = request.args.get('search_query')
    selected_n_reports = int(request.args.get('n_reports') or 0)
    words, suggestions = parse_query(search_query)
    results = find_matches(words)
    items = rows_to_items(results)

    return render_template(
        'results.html',
        search=search_query,
        selected_n_reports=selected_n_reports,
        max_n_reports=10,
        items=items,
        suggestion=" ".join(suggestions)
    )

@app.route('/duplicates')
def search_similar():
    id = int(request.args.get('id'))
    results = find_similar_2(id)
    items = rows_to_items(results)
    base_item = list(filter(lambda x: x.id == id, items))[0]

    return render_template(
        'duplicates.html',
        base_item=base_item,
        items=items
    )

def rows_to_items(results):
    items = [row[1]for row in results.iterrows()]
    for item in items:
        item.tokens = set([t for t in item.tokens if len(t) > 1])
        item.description = item.description.split('*')[0]
    return items


if __name__ == '__main__':
    app.run()
