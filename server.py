


from sanic import Sanic
from sanic import response
from jinja2 import Environment, PackageLoader, select_autoescape
import aiosqlite

import sys
from util import genearteMD5

enable_async = sys.version_info >= (3, 6)

app = Sanic(__name__)

@app.listener('before_server_start')
async def setup_db(app, loop):
    async with aiosqlite.connect("test.db") as db:
        await db.execute('DROP TABLE IF EXISTS user')
        await db.execute('DROP TABLE IF EXISTS work_info')
        await db.execute("""
            create table user (
            username varchar(20) NOT NULL primary key,
            passwd varchar(20)
            )
        """)

        await db.execute("""
            create table work_info (
            id varchar(20) NOT NULL primary key,
            username varchar(20),
            worktype varchar(20),
            status varchar(20),
            begin varchar(20),
            end varchar(20)
            )
        """)

        for i in range(1, 9):
            await db.execute("insert into user (username, \
            passwd) values ('M0{}', '123456')".format(i))
        db.commit()
        db.close()
    
template_env = Environment(
    loader=PackageLoader('auto-analysis-sanic', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    enable_async=enable_async
)

template = template_env.get_template('index.html')
template_login = template_env.get_template('login.html')
template_work = template_env.get_template('index.html')
template_result = template_env.get_template('index.html')

@app.route('/')
async def index(request):
    rendered_template = await template.render_async()
    return response.html(rendered_template)

@app.route('/login', methods=['GET']])
async def login(request):
    rendered_template = await template_login.render_async()
    return response.html(rendered_template)

@app.route('/login', methods=['POST']])
async def login(request):
    username = request.form.get('username')
    passwd = request.form.get('passwd')
    real_passwd = await get_passwd(username)
    if passwd == real_passwd:
        response.cookies['userid'] = genearteMD5(username)
        response.redirect('/work')
    else:
        response.redirect('/')

@app.route('/work')
async def work(request):
    if request.cookies.get('username'):
        rendered_template = await template_work.render_async()
        return response.html(rendered_template)
    else:
        response.redirect('/login')

@app.route('/result')
async def result(request):
    pass
