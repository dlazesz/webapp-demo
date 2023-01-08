from functools import lru_cache
from json import dumps as json_dumps
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from jinja2 import Environment, FileSystemLoader


JINJA_TEMPLATES_DIR = 'templates'


def jinja2_env_factory(templates_directory):
    """ Create a render_template() with pure JINJA2 to be as modular as possible
        INFO: https://jinja.palletsprojects.com/en/3.1.x/api/
    """
    env = Environment(loader=FileSystemLoader(templates_directory), autoescape=True)

    def render_template_fun(template_name, **variables_dict):
        template = env.get_template(template_name)
        return template.render(**variables_dict)

    return render_template_fun


render_template = jinja2_env_factory(JINJA_TEMPLATES_DIR)


# @lru_cache(10)
def render_result(res, messages, base_url, full_url, out_format='HTML', debug=False):
    # Recipe from:
    # https://stackoverflow.com/questions/7734569/how-do-i-remove-a-query-string-from-url-using-python/7734686#7734686
    full_url_parts = urlparse(full_url)
    query = parse_qs(full_url_parts.query, keep_blank_values=True)
    query.pop('page', None)  # First argument need to be str opposing bytes expected by PyCharm type hints!
    full_url_parts = full_url_parts._replace(query=urlencode(query, True), fragment='')
    full_url_wo_page = urlunparse(full_url_parts)

    if out_format == 'HTML':
        out_content = render_template('layout.html', action=base_url, full_url_wo_page=full_url_wo_page, result=res,
                                      full_url=full_url, messages=messages)
    elif out_format == 'JSON':
        out = {'result': res}
        out_content = json_dumps(out, ensure_ascii=False, indent=4)
    else:  # TSV
        out_content = '\n'.join(f'{key}\t{entry_id}\t{entry_value}' for key, val in res.items()
                                for entry_id, entry_value in val)

    # DEBUG
    if debug:
        with open('out.html', 'w', encoding='UTF-8') as fh:
            fh.write(out_content)

    return out_content
