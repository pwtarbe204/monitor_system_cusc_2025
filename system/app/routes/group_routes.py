from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify
from controller import home
from utils import globals
from utils.decorators import login_required
import time

group_bp = Blueprint('group', __name__)

def logged_in():
    if not session.get('username'):
        return False
    return True

@group_bp.route('/create_group', methods=['POST', 'GET'])
@login_required
def create_group():
    if request.method == 'POST':
        name = request.form.get("groupname")
        location = request.form.get('location')
        home.addGroupHost(globals.conn, globals.cursor, name, location)
        return redirect(url_for('group.group'))
    return redirect(url_for('group.group'))

@group_bp.route('/groups')
@login_required
def group():
    if logged_in() is True:
        try:
            raw_data = home.getGroupHost(globals.cursor)
            if raw_data['id'] == []:
                return render_template('babbix_groups.html', groups=[], active_page='groups')
            groups = []
            group_len = len(raw_data.get('id'))
            for i in range(0, group_len):
                dt = []
                for j in raw_data:
                    dt.append(raw_data.get(j)[i])
                groups.append(dt)

            return render_template(
                'babbix_groups.html',
                groups=groups,
                active_page='groups'
            )

        except Exception as e:
            import traceback
            print(f"[ERROR] group({id}): {e}")
            traceback.print_exc()
            return render_template(
                'babbix_groups.html',
                groups=[],
                active_page='groups',
                error=str(e)
            ), 500
    else:
        return redirect(url_for('auth.login'))
    
@group_bp.route('/groups/add/<int:group_id>', methods=['GET', 'POST'])
@login_required
def addAgent(group_id):
    try:
        data = []
        raw_data = home.getAgents(globals.cursor)
        for i in range(len(raw_data.get('id'))):
            items = []
            for k in raw_data:
                items.append(raw_data[k][i])
            # Giả sử index 6 là group_id
            if items[6] is not None:
                items.append(1)
            else:
                items.append(0)
            data.append(items)
            
        groupname = home.getGroupName(globals.cursor, group_id).get('group_name')
        grouplocation = home.getGroupName(globals.cursor, group_id).get('group_location')
        return render_template(
            'babbix_agents.html',
            groupname=groupname,
            grouplocation=grouplocation,
            id=group_id,
            active_page='groups'
        )

    except Exception as e:
        return render_template(
            'notfound.html'
        ), 500

@group_bp.route('/groups/<int:group_id>/<int:agent_id>', methods=['POST', 'GET'])
@login_required
def addAgentIntoGroup(group_id, agent_id):
    home.addAgentIntoGroup(globals.conn, globals.cursor, group_id, agent_id)
    return redirect(url_for('group.addAgent', group_id=group_id))

@group_bp.route('/groups/remove/<int:group_id>/<int:agent_id>')
@login_required
def removeAgent(agent_id, group_id):
    home.deleteAgent(globals.conn, globals.cursor, agent_id)
    return redirect(url_for('group.addAgent', group_id=group_id))

@group_bp.route('/groups/remove/<int:group_id>')
@login_required
def removeGroup(group_id):
    home.deleteGroup(globals.conn,globals.cursor, group_id)
    return redirect(url_for('group.group', id=1))

