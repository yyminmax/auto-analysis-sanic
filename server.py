


from sanic import Sanic
from sanic import response
from jinja2 import Environment, PackageLoader, select_autoescape

import sys

enable_async = sys.version_info >= (3, 6)

app = Sanic(__name__)

template_env = Environment(
    loader=PackageLoader('auto-analysis-sanic', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    enable_async=enable_async
)

template = template_env.get_template('index.html')
template_login = template_env.get_template('login.html')
template = template_env.get_template('index.html')
template = template_env.get_template('index.html')

@app.route('/')
async def index(request):
    pass

@app.route('/login')
async def login(request):
    pass

@app.route('/work')
async def work(request):
    pass

@app.route('/result')
async def result(request):
    pass
