import cherrypy
import json
from ..lib.access_conditions import *

from keys import *

class SurfJudgeWebInterface(object):
    def __init__(self, mount_location = '/'):
        self.mount_location = mount_location
        return


    def _populate_standard_env(self):
        env = {}
        username = cherrypy.session.get(KEY_USERNAME)
        env['global_username'] = username

        # TODO: if only normal user, dont check for ui to enhance performance
        ui = cherrypy.engine.publish(KEY_ENGINE_USER_INFO, username).pop()
        env['global_is_admin'] = ui and KEY_ROLE_ADMIN in ui.get(KEY_ROLES)
        env['global_logged_in'] = bool(username)
        return env



    @cherrypy.expose
    #@require(is_admin())
    @cherrypy.tools.render(template = 'base_template.html')
    def index(self):
        context = self._populate_standard_env()

        if context['global_username']:
            message = 'Why, you again...? Welcome back, {}!'.format(context['global_username'])
        else:
            message = 'Welcome.'

        context['title'] = 'Cool Jinja2-rendered file'
        context['description'] = 'Some description of this awesome file'
        context['message'] = message
        return context


    @cherrypy.expose
    #@require(is_admin()) # later ask for judge or similar
    @cherrypy.tools.render(template='judge_panel.html')
    def judge_panel(self):
        data = self._populate_standard_env()
        data['judge_name'] = 'Christian'
        data['judge_number'] = '1234'
        data['surfer_colors'] = ['red', 'blue']
        data['n_surfers'] = len(data['surfer_colors'])
        data['n_waves'] = 10
        return data


    @cherrypy.expose
    @require(has_roles(KEY_ROLE_JUDGE))
    def do_query_scores(self):
        query_info = {}
        scores = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_SCORES, query_info).pop()
        return json.dumps(scores)

    @cherrypy.expose
    def do_insert_score(self):
        score = {'wave': 1,
                 'score': 5,
                 'color': 'blue',
                 'judge_id': '1'}
        res = cherrypy.engine.publish(KEY_ENGINE_DB_INSERT_SCORE, score).pop()
        return res

    @cherrypy.expose
    #@require(is_admin())
    def javascript_request(self, parameter = None):
        #database request
        #store in some variable
        #return the variable
        result = 'hallo'
        return result


    @cherrypy.expose
    @cherrypy.tools.render(template = 'simple_message.html')
    def simple_message(self, msg = None):
        env = {}
        env['message'] = msg
        return env
