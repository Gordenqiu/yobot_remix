import asyncio
import json
import logging
import os
import datetime
import aiohttp
from urllib.parse import urljoin

from playhouse.shortcuts import model_to_dict
from quart import Quart, jsonify, redirect, request, session, url_for

from .templating import render_template
from .ybdata import Clan_group, User

_returned_query_fileds = [
    User.qqid,
    User.nickname,
    User.clan_group_id,
    User.authority_group,
    User.last_login_time,
    User.last_login_ipaddr,
]

logger = logging.getLogger(__name__)

class Setting:
    Passive = False
    Active = False
    Request = True

    def __init__(self,
                 glo_setting,
                 bot_api,
                 boss_id_name,
                 *args, **kwargs):
        self.setting = glo_setting
        self.boss_id_name = boss_id_name

    def _get_users_json(self, req_querys: dict):
        querys = []
        if req_querys.get('qqid'):
            querys.append(
                User.qqid == req_querys['qqid']
            )
        if req_querys.get('clan_group_id'):
            querys.append(
                User.clan_group_id == req_querys['clan_group_id']
            )
        if req_querys.get('authority_group'):
            querys.append(
                User.authority_group == req_querys['authority_group']
            )
        users = User.select(
            User.qqid,
            User.nickname,
            User.clan_group_id,
            User.authority_group,
            User.last_login_time,
            User.last_login_ipaddr,
        ).where(
            User.deleted == False,
            *querys,
        ).paginate(
            page=req_querys['page'],
            paginate_by=req_querys['page_size']
        )
        return json.dumps({
            'code': 0,
            'data': [model_to_dict(u, only=_returned_query_fileds) for u in users],
        })

    def register_routes(self, app: Quart):

        @app.route(
            urljoin(self.setting['public_basepath'], 'admin/setting/'),
            methods=['GET'])
        async def yobot_setting():
            if 'yobot_user' not in session:
                return redirect(url_for('yobot_login', callback=request.path))
            user = User.get_by_id(session['yobot_user'])
            if user.authority_group >= 10:
                if not user.authority_group >= 100:
                    uathname = '公会战管理员'
                else:
                    uathname = '成员'
                return await render_template(
                    'unauthorized.html',
                    limit='主人',
                    uath=uathname,
                )
            return await render_template(
                'admin/setting.html',
            )

        @app.route(
            urljoin(self.setting['public_basepath'], 'admin/setting/api/'),
            methods=['GET', 'PUT'])
        async def yobot_setting_api():
            if 'yobot_user' not in session:
                return jsonify(
                    code=10,
                    message='Not logged in',
                )
            user = User.get_by_id(session['yobot_user'])
            if user.authority_group >= 100:
                return jsonify(
                    code=11,
                    message='Insufficient authority',
                )
            if request.method == 'GET':
                settings = self.setting.copy()
                boss_id_name = self.boss_id_name.copy()
                del settings['dirname']
                del settings['verinfo']
                del settings['host']
                del settings['port']
                del settings['access_token']
                del settings['AppID']
                return jsonify(
                    code=0,
                    message='success',
                    settings=settings,
                    boss_id_name=boss_id_name
                )
            elif request.method == 'PUT':
                req = await request.get_json()
                if req.get('csrf_token') != session['csrf_token']:
                    return jsonify(
                        code=15,
                        message='Invalid csrf_token',
                    )
                new_setting = req.get('setting')
                if new_setting is None:
                    return jsonify(
                        code=30,
                        message='Invalid payload',
                    )
                self.setting.update(new_setting)
                save_setting = self.setting.copy()
                del save_setting['dirname']
                del save_setting['verinfo']
                config_path = os.path.join(
                    self.setting['dirname'], 'yobot_config.json')
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(save_setting, f, indent=4)
                return jsonify(
                    code=0,
                    message='success',
                )

        @app.route(
            urljoin(self.setting['public_basepath'], 'admin/pool-setting/'),
            methods=['GET'])
        async def yobot_pool_setting():
            if 'yobot_user' not in session:
                return redirect(url_for('yobot_login', callback=request.path))
            user = User.get_by_id(session['yobot_user'])
            if user.authority_group >= 10:
                if not user.authority_group >= 100:
                    uathname = '公会战管理员'
                else:
                    uathname = '成员'
                return await render_template(
                    'unauthorized.html',
                    limit='主人',
                    uath=uathname,
                )
            return await render_template('admin/pool-setting.html')

        @app.route(
            urljoin(self.setting['public_basepath'],
                    'admin/pool-setting/api/'),
            methods=['GET', 'PUT'])
        async def yobot_pool_setting_api():
            if 'yobot_user' not in session:
                return jsonify(
                    code=10,
                    message='Not logged in',
                )
            user = User.get_by_id(session['yobot_user'])
            if user.authority_group >= 10:
                return jsonify(
                    code=11,
                    message='Insufficient authority',
                )
            if request.method == 'GET':
                with open(os.path.join(self.setting['dirname'], 'pool3.json'),
                          'r', encoding='utf-8') as f:
                    settings = json.load(f)
                return jsonify(
                    code=0,
                    message='success',
                    settings=settings,
                )
            elif request.method == 'PUT':
                req = await request.get_json()
                if req.get('csrf_token') != session['csrf_token']:
                    return jsonify(
                        code=15,
                        message='Invalid csrf_token',
                    )
                new_setting = req.get('setting')
                if new_setting is None:
                    return jsonify(
                        code=30,
                        message='Invalid payload',
                    )
                with open(os.path.join(self.setting['dirname'], 'pool3.json'),
                          'w', encoding='utf-8') as f:
                    json.dump(new_setting, f, ensure_ascii=False, indent=2)
                return jsonify(
                    code=0,
                    message='success',
                )

        @app.route(
            urljoin(self.setting['public_basepath'], 'admin/users/'),
            methods=['GET'])
        async def yobot_users_managing():
            if 'yobot_user' not in session:
                return redirect(url_for('yobot_login', callback=request.path))
            user = User.get_by_id(session['yobot_user'])
            if user.authority_group >= 10:
                if not user.authority_group >= 100:
                    uathname = '公会战管理员'
                else:
                    uathname = '成员'
                return await render_template(
                    'unauthorized.html',
                    limit='主人',
                    uath=uathname,
                )
            return await render_template('admin/users.html')

        @app.route(
            urljoin(self.setting['public_basepath'], 'admin/users/api/'),
            methods=['POST'])
        async def yobot_users_api():
            if 'yobot_user' not in session:
                return jsonify(
                    code=10,
                    message='Not logged in',
                )
            user = User.get_by_id(session['yobot_user'])
            if user.authority_group >= 10:
                return jsonify(
                    code=11,
                    message='Insufficient authority',
                )
            try:
                req = await request.get_json()
                if req is None:
                    return jsonify(
                        code=30,
                        message='Invalid payload',
                    )
                if req.get('csrf_token') != session['csrf_token']:
                    return jsonify(
                        code=15,
                        message='Invalid csrf_token',
                    )
                action = req['action']
                if action == 'get_data':
                    return await asyncio.get_event_loop().run_in_executor(
                        None,
                        self._get_users_json,
                        req['querys'],
                    )

                elif action == 'modify_user':
                    data = req['data']
                    m_user: User = User.get_or_none(qqid=data['qqid'])
                    if ((m_user.authority_group <= user.authority_group) or
                            (data.get('authority_group', 999)) <= user.authority_group):
                        return jsonify(code=12, message='Exceed authorization is not allowed')
                    if data.get('authority_group') == 1:
                        self.setting['super-admin'].append(data['qqid'])
                        save_setting = self.setting.copy()
                        del save_setting['dirname']
                        del save_setting['verinfo']
                        config_path = os.path.join(
                            self.setting['dirname'], 'yobot_config.json')
                        with open(config_path, 'w', encoding='utf-8') as f:
                            json.dump(save_setting, f, indent=4)
                    if m_user is None:
                        return jsonify(code=21, message='user not exist')
                    for key in data.keys():
                        setattr(m_user, key, data[key])
                    m_user.save()
                    return jsonify(code=0, message='success')
                elif action == 'delete_user':
                    user = User.get_or_none(qqid=req['data']['qqid'])
                    if user is None:
                        return jsonify(code=21, message='user not exist')
                    user.clan_group_id = None
                    user.authority_group = 999
                    user.password = None
                    user.deleted = True
                    user.save()
                    return jsonify(code=0, message='success')
                else:
                    return jsonify(code=32, message='unknown action')
            except KeyError as e:
                return jsonify(code=31, message=str(e))

        @app.route(
            urljoin(self.setting['public_basepath'], 'admin/groups/'),
            methods=['GET'])
        async def yobot_groups_managing():
            if 'yobot_user' not in session:
                return redirect(url_for('yobot_login', callback=request.path))
            user = User.get_by_id(session['yobot_user'])
            if user.authority_group >= 10:
                if not user.authority_group >= 100:
                    uathname = '公会战管理员'
                else:
                    uathname = '成员'
                return await render_template(
                    'unauthorized.html',
                    limit='主人',
                    uath=uathname,
                )
            return await render_template('admin/groups.html')

        @app.route(
            urljoin(self.setting['public_basepath'], 'admin/groups/api/'),
            methods=['POST'])
        async def yobot_groups_api():
            if 'yobot_user' not in session:
                return jsonify(
                    code=10,
                    message='Not logged in',
                )
            user = User.get_by_id(session['yobot_user'])
            if user.authority_group >= 10:
                return jsonify(
                    code=11,
                    message='Insufficient authority',
                )
            try:
                req = await request.get_json()
                if req is None:
                    return jsonify(
                        code=30,
                        message='Invalid payload',
                    )
                if req.get('csrf_token') != session['csrf_token']:
                    return jsonify(
                        code=15,
                        message='Invalid csrf_token',
                    )
                action = req['action']
                if action == 'get_data':
                    groups = []
                    for group in Clan_group.select().where(
                        Clan_group.deleted == False,
                    ):
                        groups.append({
                            'group_id': group.group_id,
                            'group_name': group.group_name,
                            'game_server': group.game_server,
                        })
                    return jsonify(code=0, data=groups)
                if action == 'drop_group':
                    User.update({
                        User.clan_group_id: None,
                    }).where(
                        User.clan_group_id == req['group_id'],
                    ).execute()
                    Clan_group.delete().where(
                        Clan_group.group_id == req['group_id'],
                    ).execute()
                    return jsonify(code=0, message='ok')
                else:
                    return jsonify(code=32, message='unknown action')
            except KeyError as e:
                return jsonify(code=31, message=str(e))


        @app.route(urljoin(self.setting['public_basepath'], 'admin/setting/auto_get_boss_data/'), methods=['POST'])
        async def auto_get_boss_data():
            req = await request.get_json()
            if req.get('csrf_token') != session['csrf_token']:
                return jsonify(code=15, message='Invalid csrf_token' )

            new_setting = self.setting.copy()
            new_boss_id_name:dict = self.boss_id_name.copy()
            back_msg = []

            date = datetime.date.today()
            d_year = date.year
            d_month = date.month
            url = 'https://pcr.satroki.tech/api/Quest/GetClanBattleInfos?s={}'

            boss_infos:dict = self.setting['boss']
            for server, _ in boss_infos.items():
                real_url = url.format(server)
                try:
                    async with aiohttp.ClientSession() as ses:
                        async with ses.get(real_url) as resp:
                            infos = await resp.json()
                    success_flag = False
                    for info in infos:
                        if info["year"] != d_year or info["month"] != d_month: continue
                        success_flag = True
                        new_setting['boss_id'][server], new_setting['boss'][server], server_level_by_cycle = [], [], []
                        boss_phase = info["phases"][0]["bosses"]
                        for bp in boss_phase: new_setting['boss_id'][server].append(str(bp["unitId"]))
                        for stage in range(len(info["phases"])):
                            stage_info = info["phases"][stage]
                            new_setting['boss'][server].append([])
                            server_level_by_cycle.append(stage_info['lapFrom'])
                            for boss_num in range(len(stage_info["bosses"])):
                                boss_info = stage_info["bosses"][boss_num]
                                new_setting['boss'][server][stage].append(boss_info['hp'])
                                if str(boss_info['unitId']) not in new_boss_id_name[str(boss_num + 1)]:
                                    new_boss_id_name[str(boss_num + 1)][str(boss_info['unitId'])] = boss_info['name']
                        new_setting['level_by_cycle'][server] = []
                        for stage in range(len(server_level_by_cycle)):
                            if stage < len(server_level_by_cycle) - 1:
                                new_setting['level_by_cycle'][server].append([int(server_level_by_cycle[stage]), int(server_level_by_cycle[stage + 1]) - 1])
                            else:
                                new_setting['level_by_cycle'][server].append([int(server_level_by_cycle[stage]), 999])
                        break
                    if success_flag:
                        back_msg.append(f'{server}更新当期boss数据成功！')
                    else:
                        back_msg.append(f'{server}更新当期boss数据失败，可能是获取不到当期数据。')
                except Exception as e:
                    back_msg.append(f'{server}更新当期boss数据失败:\n{e}')
            self.setting.update(new_setting)
            save_setting = self.setting.copy()
            del save_setting['dirname']
            del save_setting['verinfo']
            config_path = os.path.join(self.setting['dirname'], 'yobot_config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(save_setting, f, indent=4)

            self.boss_id_name.update(new_boss_id_name)
            save_boss_id_name = self.boss_id_name.copy()
            boss_id_name_path = os.path.join(self.setting['dirname'], 'BossIdAndName.json')
            with open(boss_id_name_path, 'w', encoding='utf-8') as f:
                json.dump(save_boss_id_name, f, indent=4, ensure_ascii=False)

            task_list = []
            for boss_infos in new_boss_id_name.values():
                for boss_id in boss_infos.keys():
                    icon_path = os.path.join(os.path.dirname(self.setting['dirname']), 'public', 'libs', 'yocool@final', 'princessadventure', 'boss_icon', f'{boss_id}.webp')
                    if not os.path.exists(icon_path): task_list.append(download_icon(icon_path, boss_id))
            await asyncio.gather(*task_list)

            return jsonify(
                code=0,
                message='<br/>'.join(back_msg),
            )

async def download_icon(icon_path, boss_id):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f'https://redive.estertion.win/icon/unit/{boss_id}.webp') as resp:
            data = await resp.read()
    with open(icon_path, 'wb') as img:
        img.write(data)
    logger.info(f'{boss_id}.webp下载成功')
