from secrets import compare_digest
from json import dumps as json_dumps
import uvicorn

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, Request, Response, Depends, HTTPException

from template import render_result
from sql import get_db, table_objs, table_column_objs


app = FastAPI()


users = {
    'john': 'hello',
    'susan': 'bye'
}


security = HTTPBasic()
"""
OR
request.environ.get('REMOTE_USER')
request.environ.pop('HTTP_X_PROXY_REMOTE_USER', None)
"""


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    """INFO: https://fastapi.tiangolo.com/advanced/security/http-basic-auth/"""
    if credentials.username in users and compare_digest(users.get(credentials.username), credentials.password):
        return credentials.username

    raise HTTPException(
        status_code=401,
        detail='Incorrect email or password',
        headers={'WWW-Authenticate': 'Basic'},
    )


class InvalidUsage(Exception):
    """INFO: https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(self, message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.exception_handler(InvalidUsage)
async def exception_handler(_: Request, exc: InvalidUsage):
    """INFO: https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers"""
    result_json = json_dumps(exc.to_dict(), ensure_ascii=False, indent=4)
    return Response(result_json, exc.status_code, media_type='application/json')


@app.on_event('startup')
def startup_event():
    pass


@app.get('/')
async def api_data(request: Request, username: str = Depends(get_current_username)):
    if username is not None:
        print('alma')

    # print(await request.json())
    # print(await request.form())

    # Demo SQL query
    with get_db() as db:
        print(db.query(table_column_objs[('prevcons', 'prev')]).distinct().all())

    # Handle multiple params!
    print(request.query_params.multi_items())

    # Extract params from Request
    other_params, base_url, full_url = request.query_params, str(request.base_url), str(request.url)

    # Request param to bool
    regex_val = other_params.get('val', default='false').lower() == 'true'

    exc_tb = []
    """
    try:
        raise InvalidUsage('msg', status_code=400)
    except InvalidUsage as e:
        exc_tb.append((e.__traceback__, e.message, e.status_code))
    """

    messages = []
    if len(exc_tb) > 0:
        # Raise the first exception (REST API JSON, CLI) or flash all (WebUI)
        if other_params['format'] != 'HTML':
            tb, message, status_code = exc_tb[0]
            raise InvalidUsage(message, status_code=status_code).with_traceback(tb)
        else:
            for _, message, _ in exc_tb:
                messages.append(message)

    format_param = other_params.get('format', 'HTML')
    result = render_result(other_params, messages, base_url, full_url, format_param)
    if format_param == 'HTML' and len(base_url) > 0:
        result = Response(content=result, media_type='text/html')
    elif format_param == 'JSON' and len(base_url) > 0:
        result = Response(content=result, media_type='application/json')
    elif format_param == 'TSV' and len(base_url) > 0:
        result = Response(content=result, media_type='text/tab-separated-values',
                          headers={'Content-Disposition': 'attachment; filename=result.tsv'})
    return result

if __name__ == '__main__':
    uvicorn.run('fast_api:app', host='0.0.0.0', port=5000, workers=1)
