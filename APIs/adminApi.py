from flask import Flask, jsonify
from flask import render_template
from flask import request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def welcome():
    return redirect(url_for('api'))

@app.route('/API')
def api():
    return "Welcome to the admin API"


@app.route('/API/addBuilding', methods=['POST'])
def addBuilding():
    # function that receives building information and inserts it in db
    request.form["id"]
    request.form["name"]
    request.form["latitude"]
    request.form["longitude"]

    



    # dúvida: temos que fazer validação dos edifícios?


@app.route('/API/books/<author>', methods=['GET'])
def book_by_auth(author):
    list_book = db.listBooksAuthor(str(author))
    if not list_book:
        abort()
    return render_template("listBooksTemplate.html", bookList=list_book)


@app.route('/API/books/<author>/<year>', methods=['GET'])
def book_by_authnyear(author, year):
    list_year = db.listBooksYear(int(year))
    list_book = db.listBooksAuthor(str(author))
    for item in list_book:
        if item not in list_year:
            list_book.remove(item)
    if not list_book:
        abort()
    return render_template("listBooksTemplate.html", bookList=list_book)


@app.route('/API/authors', methods=['GET'])
def list_authors():
    if 'author' in request.args:
        # confirm if author is in database
        list_author = db.listBooksAuthor(request.args['author'])
        if not list_author:
            return "Author not in database"
        else:
            return "Author is in database, go to /API/books?author=<author_name> to see its books"
    else:
        # show all authors
        list_author = db.listAllAuthors()
        return str(list_author)


@app.errorhandler(404)
def abort(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == '__main__':
    app.run()
