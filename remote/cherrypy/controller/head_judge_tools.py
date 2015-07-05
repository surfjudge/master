import cherrypy
import json
from ..lib.access_conditions import *
from . import CherrypyWebInterface

from keys import *

class HeadJudgeWebInterface(CherrypyWebInterface):


    @cherrypy.expose
    @cherrypy.tools.render(template = 'headjudge/headjudge_panel.html')
    def index(self):
        context = self._standard_env()
        heat_info = cherrypy.engine.publish(KEY_ENGINE_SM_GET_ACTIVE_HEAT_INFO, None).pop()
        tournaments = set()
        for heat in heat_info.values():
            tournaments.add(heat['tournament_id'])
        for tournament_id in tournaments:
            panel_html = self.render_html(context = self.get_tournament_activity_panel(tournament_id), template = 'headjudge/activity_panel.html')
            context.setdefault('panels', []).append(panel_html)
        return context


    ##############
    # REST stuff #
    ##############

    @cherrypy.expose
    def do_activate_heat(self, heat_id = None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)
        query_info = {'heat_id': heat_id}

        # get heat_info from database
        heat_info = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, query_info).pop()
        if len(heat_info) > 0:
            heat_info = heat_info[0]

        heat_info[KEY_HEAT_ID] = heat_id
        judges = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_JUDGES_FOR_HEAT, heat_id).pop()
        for judge in judges:
            if judge[KEY_HEAT_ID] != heat_id:
                continue
            judge_id = judge[KEY_JUDGE_ID]
            first_name = judge['first_name']
            last_name = judge['last_name']
            username = judge['username']
            heat_info.setdefault('judges', {})[judge_id] = {KEY_HEAT_ID: heat_id,
                                                            KEY_JUDGE_ID: judge_id,
                                                            'judge_first_name': first_name,
                                                            'judge_last_name': last_name,
                                                            'judge_username': username}
        res = cherrypy.engine.publish(KEY_ENGINE_SM_ACTIVATE_HEAT, heat_id, heat_info).pop()
        return res

    @cherrypy.expose
    def do_deactivate_heat(self, heat_id = None, **kwargs):
        if heat_id is None:
            return
        heat_id = int(heat_id)

        res = cherrypy.engine.publish(KEY_ENGINE_SM_DEACTIVATE_HEAT, heat_id).pop()
        return res


    @cherrypy.expose
    @cherrypy.tools.render(template='headjudge/activity_panel.html')
    def get_tournament_activity_panel(self, tournament_id=None):
        context = self._standard_env()

        if tournament_id is None:
            return ''
        heat_info = cherrypy.engine.publish(KEY_ENGINE_DB_RETRIEVE_HEAT_INFO, {'tournament_id': tournament_id}).pop()
        if len(heat_info) == 0:
            return ''

        context['tournament_name'] = heat_info[0]['tournament_name']
        categories = {}
        cid2heats = {}
        for heat in heat_info:
            cid = heat['category_id']
            categories[cid] = {'id': cid, 'name': heat['category_name']}
            cid2heats.setdefault(cid, {})[heat['heat_id']] = {'id': heat['heat_id'], 'name': heat['heat_name']}

        context['categories'] = sorted(categories.values(), key=lambda x:x['name'])
        context['heats'] = {}
        for cid, heats in cid2heats.items():
            print heats.values()
            context['heats'][cid] = sorted(heats.values(), key=lambda x:x['name'])
        return context
