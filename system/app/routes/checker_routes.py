from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify
from controller import home
import time
from utils import globals
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.decorators import login_required

checker_bp = Blueprint('checker', __name__)

@checker_bp.route('/checker')
@login_required
def checker():
    return render_template('babbix_checker.html', active_page='checker')

@checker_bp.route("/ping")
def ping():
    return jsonify({"message": "Kết nối thành công tới server!"})


@checker_bp.route('/check_local', methods=['POST'])
@login_required
def check_local():
    time.sleep(0.2)
    data = request.get_json()
    src_ip = data.get("selectedIP")
    group_id = data.get("groupID")
    agents = data.get("agents")

    print(agents)

    url = f'http://{src_ip}:5001/check_local' 
    print(url)
    dt = {"ips": agents}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=dt, headers=headers)

    return jsonify(response.json())


@checker_bp.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    url_check = data.get("urls", [])
    agent_check = data.get("agents", [])
    
    results = asyncio.run(run_checks(agent_check, url_check))

    return jsonify(results)

async def check_agent(session, agent, url_checker):
    base_url = f"http://{agent}:5001/ping"
    response_time = 0
    rtt = 0
    count = 0
    status = "unknown"

    for target_url in url_checker:
        try:
            payload = {"url": target_url}
            async with session.post(base_url, json=payload, timeout=5) as response:
                data = await response.json()
                rtt_value = data.get('rtt', -1)
                load_time_value = data.get('load_time', -1)

                if rtt_value == -1 or load_time_value == -1:
                    continue

                rtt += float(rtt_value)
                response_time += float(load_time_value)
                count += 1
                status = data.get('status', 'unknown')
        except Exception as e:
            print(f"[ERROR] Agent {agent}, URL {target_url}:{e}")
            continue
    if count == 0:
        return {"host": agent, "load_time": -1, "rtt": -1, "status" : "fail"}
    return {
        "host" : agent,
        "load_time" : round(response_time / count),
        "rtt": round(rtt / count),
        "status" : status
    }
#------------------------------------------#
async def run_checks(agent_list, url_check):
    async with aiohttp.ClientSession() as session:
        task_1 = [check_agent(session, agent, url_check) for agent in agent_list]
        return await asyncio.gather(*task_1)
#------------------------------------------#

#-------------------------------------------#
#Check URL có an toàn hay không
def isSafe(url):
    try:
        submit_resp = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers={"x-apikey": '2f1372eb6b88806db5a9c04a356acd8abb374ba1f0fac36bc3d17ba507f46e32'},
            data={"url": url}
        )
        submit_data = submit_resp.json()
        analysis_id = submit_data["data"]["id"]

        time.sleep(10)

        report_resp = requests.get(
            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
            headers={"x-apikey": '2f1372eb6b88806db5a9c04a356acd8abb374ba1f0fac36bc3d17ba507f46e32'}
        )
        report_data = report_resp.json()
        stats = report_data["data"]["attributes"]["stats"]

        result = {
            "url": url,
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "safety" : 'unsafe' if stats.get('malicious', 0) > 0 or stats.get('suspicious', 0) > 0 else 'safe'
        }
        return result
    except Exception as e:
        return {"url": url, "error": str(e)}
#-------------------------------------------#
@checker_bp.route('/check_url_is_safe', methods=['POST'])
def check_url_is_safe():
    data = request.get_json()
    url_check = data.get("urls", [])
    with ThreadPoolExecutor(max_workers=4) as executor:
        urlIsSafe = list(executor.map(isSafe, url_check))
    print(urlIsSafe)
    return jsonify(urlIsSafe)