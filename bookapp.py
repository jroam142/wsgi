import re
import traceback

from bookdb import BookDB

DB = BookDB()


def book(book_id):
    specific_book = DB.title_info(book_id)
    if not specific_book:
        raise NameError

    body = """<div><h1>{title}</h1>\n
            <h2>By: {author}</h2>
            <h4>Published By: {publisher}</h4>\n
            <h4>isbn: {isbn}</h4>\n</div>"""
            
    return body.format(title=specific_book['title'], 
                       author=specific_book['author'],
                       publisher=specific_book['publisher'],
                       isbn=specific_book['isbn'])


def books():
    all_books = DB.titles()
    body = ['<h1>My Bookshelf</h1>', '<ul>']

    item_template = "<li><a href='/book/{id}'>{title}</a></li>"
    for book in all_books:
        body.append(item_template.format(**book))

    return '\n'.join(body)

def resolve_path(path):
    funcs = {
            "": books,
            'book': book,
            }

    path = path.strip('/').split('/')

    func_name = path[0]
    args=path[1:]

    try:
        func = funcs[func_name]
    except KeyError:
        raise NameError

    return func, args


def application(environ, start_response):
    headers = [('Content-type', 'text/html')]

    try:
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError
        func, args = resolve_path(path)
        body = func(*args)
        status = "200 OK"
    except NameError:
        status = "404 Not Found"
        body = '<h2>Not Found</h1>'
    except Exception:
        status = "500 Internal Sever Error"
        body = "</h1>Internal Server Error</h1>"
        print(traceback.format_exc())
    finally:
        headers.append(('content-length', str(len(body))))
        start_response(status, headers)
        return [body.encode('utf8')]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
