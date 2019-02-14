from flask import Flask, url_for, render_template
from flask import flash, render_template, request, redirect
from model.inverse_index import parse_query, find_matches
from model.duplicates import find_similar, find_similar_2, get_groups_with_n_plus
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/results')
def search_results():
    search_query = request.args.get('search_query')
    words, suggestions = parse_query(search_query)
    results = find_matches(words)
    items = rows_to_items(results)

    return render_template(
        'results.html',
        search=search_query,
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

@app.route('/groups')
def search_groups():
    search_query = request.args.get('search_query') or ''
    selected_n_reports = int(request.args.get('n_reports') or 0)
    words, suggestions = parse_query(search_query)
    results = find_matches(words)
    groups = get_groups_with_n_plus(results, selected_n_reports)
   
    items = [group_to_item(group) for group in groups]

    return render_template(
        'groups.html',
        search=search_query,
        selected_n_reports=selected_n_reports,
        max_n_reports=25,
        items=items,
        suggestion=" ".join(suggestions)
    )

def group_to_item(group):
    first_row = next(group.iterrows())
    print(first_row)
    item = first_row[1]

    item.n_duplicates = len(group)
    item.tokens = set([t for t in item.tokens if len(t) > 1])
    item.description = item.description.split('*')[0]

    return item

    

def rows_to_items(results):
    items = [row[1]for row in results.iterrows()]
    for item in items:
        item.tokens = set([t for t in item.tokens if len(t) > 1])
        item.description = item.description.split('*')[0]
    return items


if __name__ == '__main__':
    app.run()
