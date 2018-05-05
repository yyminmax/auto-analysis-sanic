

from sanic import Sanic, response
from jinja2 import Environment, FileSystemLoader, select_autoescape
import aiosqlite

import asyncio.subprocess
from time import strftime, localtime

enable_async = sys.version_info >= (3, 6)

app = Sanic(__name__)

@app.middleware('response')
async def custom_banner(request, response):
    response.headers["Server"] = "Fake-Server"

@app.listener('before_server_start')
async def setup_db(app, loop):
    async with aiosqlite.connect(':memory:') as db:
        await db.executescript("""
            DROP TABLE IF EXISTS work;
            DROP TABLE IF EXISTS result;

            CREATE TABLE IF EXISTS work (
                project,
                subject,
                teacher,
                numsample,
                workrequire
            );

            CREATE TABLE IF EXISTS result (
                id char(7) NOT NULL primary key,
                project,
                subject,
                status,
                worktype,
                begin,
                end
            );
        """)
        
        await db.commit()

template_env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml']),
    enable_async=enable_async
)

template_work = template_env.get_template('work.html')
template_result = template_env.get_template('result.html')
template_work_subject = template_env.get_template('subject.html')

async def get_workinfo(workinfo_html):
    create = asyncio.create_subprocess_shell('bash script/demo3.sh > ' + workinfo_html)
    proc = await create

    await proc.wait()
    w_html = open(workinfo_html, 'r')
    soup = BeautifulSoup(w_html.read())
    tag_list = soup.findAll('td')
    table = []
    # temp_table = [project, subject, teacher, numsample, workrequire]
    temp_table = [''] * 5
    for i in range(3, len(tag_list), 25):
        # judge MPL or MbPL
        if tag_list[i].text.startswith('MbPL') or tag_list[i].text.startswith('MPL'):
            temp_table[1] = tag_list[i].text
            for j in range(i, i+25):
                if j % 25 == 4:
                    temp_table[4] = tag_list[j].text
                if j % 25 == 5:
                    temp_table[3] = tag_list[j].text
                if j % 25 == 8:
                    temp_table[2] = tag_list[j].text
                if j % 25 == 12:
                    temp_table[0] = tag_list[j].text
                    table.append(tuple([t.strip() for t in temp_table]))
                    temp_table = []
    return table

async def insert_table_into_db(table):
    async with aiosqlite.connect(':memory:') as db:
        db.execute('INSERT INTO result(project, subject, status, \
                    worktype, begin) VALUES (?,?,?,?,?)', table)
        await db.commit()

async def get_result_info_from_db():
    async with aiosqlite.connect(':memory:') as db:
        db.execute('SELECT * FROM result ORDER BY begin')
        return db.fetchall()

@app.route('/')
async def work(request):
    table = await get_workinfo()
    rendered_template = await template_work.render_async(
        table=table
    )
    return response.html(rendered_template)

@app.route('/result', methods=['GET'])
async def result_get(request):
    table = await get_result_info_from_db()
    rendered_template = await template_result.render_async(
        table=table
    )
    return response.html(rendered_template)

@app.route('/result', methods=['POST'])
async def result_get(request):
    project = request.form.get('project')
    subject = request.form.get('subject')
    worktype = request.form.get('worktype')
    map = request.form.get('map')
    insert_table = (project, subject, 'Queuing', worktype, \
                    strftime("%Y-%m-%d %H:%M:%S", localtime())
    table = await get_result_info_from_db(insert_table)
    rendered_template = await template_result.render_async(
        table=table
    )
    return response.html(rendered_template)
    
