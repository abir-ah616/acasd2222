import requests
import json
import os
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from bot_api import (
    check_banned_status, 
    get_player_status, 
    send_invite_two_players, 
    send_spam_requests, 
    send_spam_invites, 
    send_team_attack
)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex()) 

BOT_API_URL = "http://127.0.0.1:8080/command"

@app.route('/')
def index():
    """Renders the main emote bot control panel page."""
    return render_template('index.html')

@app.route('/status')
def status_page():
    """Renders the status check page."""
    return render_template('status.html')

@app.route('/check')
def check_page():
    """Renders the ban status check page."""
    return render_template('check.html')

@app.route('/invite')
def invite_page():
    """Renders the invite anyone page."""
    return render_template('invite.html')

@app.route('/sm')
def sm_page():
    """Renders the spam join requests page."""
    return render_template('sm.html')

@app.route('/x')
def x_page():
    """Renders the spam invites page."""
    return render_template('x.html')

@app.route('/attack')
def attack_page():
    """Renders the team attack page."""
    return render_template('attack.html')

@app.route('/action', methods=['POST'])
def handle_action():
    """Handles all form submissions from the new UI."""
    try:
        action = request.form.get('action')
        payload_str = request.form.get('payload')
        
        if not action or payload_str is None:
            flash('Invalid request from client.', 'danger')
            return redirect(url_for('index'))

        bot_payload = {'action': action}
        
        data = json.loads(payload_str)

        if action == 'emote':
            bot_payload.update(data)
            if not bot_payload.get('emote_id') or not bot_payload.get('player_ids'):
                raise ValueError("Emote ID and Player IDs are required.")
            flash(f"Sending emote {bot_payload['emote_id']} to {len(bot_payload['player_ids'])} player(s)...", 'success')

        elif action == 'emote_batch':
            if not isinstance(data, list):
                raise ValueError("A list of assignments is required for emote_batch.")
            bot_payload['assignments'] = data
            flash(f"Sending batch of {len(bot_payload['assignments'])} assigned emotes...", 'success')
            
        elif action == 'join_squad':
            bot_payload.update(data)
            if not bot_payload.get('team_code'):
                 raise ValueError("Team Code is required.")
            flash(f"Attempting to join squad {bot_payload.get('team_code')}...", 'success')

        elif action == 'quick_invite':
            bot_payload.update(data)
            if not bot_payload.get('player_id'):
                 raise ValueError("Your Main Account UID is required.")
            flash('Creating squad and sending invite...', 'success')

        elif action == 'leave_squad':
            bot_payload.update(data)
            flash('Telling bot to leave squad...', 'info')
        
        else:
            flash(f'Unknown action: {action}', 'danger')
            return redirect(url_for('index'))

        response = requests.post(BOT_API_URL, json=bot_payload, timeout=10)
        
        if response.status_code == 200:
            flash(response.json().get('message', 'Command sent successfully!'), 'success')
        else:
            flash(f"Error from bot: {response.status_code} - {response.json().get('error', 'Unknown error')}", 'danger')

    except requests.exceptions.ConnectionError:
        flash('Could not connect to the bot API. Is main.py running?', 'danger')
    except (ValueError, json.JSONDecodeError) as e:
        flash(f'Invalid data provided: {e}', 'danger')
    except Exception as e:
        flash(f'An unexpected error occurred: {e}', 'danger')

    return redirect(url_for('index'))

@app.route('/api/status', methods=['POST'])
def api_status():
    """API endpoint for checking player status."""
    try:
        data = request.get_json()
        uid = data.get('uid')
        
        if not uid:
            return jsonify({"status": "error", "message": "UID is required"}), 400
        
        result = get_player_status(uid)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/check', methods=['POST'])
def api_check():
    """API endpoint for checking ban status."""
    try:
        data = request.get_json()
        uid = data.get('uid')
        
        if not uid:
            return jsonify({"status": "error", "message": "UID is required"}), 400
        
        result = check_banned_status(uid)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/invite', methods=['POST'])
def api_invite():
    """API endpoint for sending invite to two players."""
    try:
        data = request.get_json()
        your_uid = data.get('your_uid')
        target_uid = data.get('target_uid')
        
        if not your_uid or not target_uid:
            return jsonify({"status": "error", "message": "Both UIDs are required"}), 400
        
        result = send_invite_two_players(your_uid, target_uid)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sm', methods=['POST'])
def api_sm():
    """API endpoint for spam join requests."""
    try:
        data = request.get_json()
        uid = data.get('uid')
        
        if not uid:
            return jsonify({"status": "error", "message": "UID is required"}), 400
        
        result = send_spam_requests(uid)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/x', methods=['POST'])
def api_x():
    """API endpoint for spam invites."""
    try:
        data = request.get_json()
        uid = data.get('uid')
        
        if not uid:
            return jsonify({"status": "error", "message": "UID is required"}), 400
        
        result = send_spam_invites(uid)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/attack', methods=['POST'])
def api_attack():
    """API endpoint for team attack."""
    try:
        data = request.get_json()
        team_code = data.get('team_code')
        
        if not team_code:
            return jsonify({"status": "error", "message": "Team code is required"}), 400
        
        result = send_team_attack(team_code)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("CLOUD ENGINE Bot Web Panel")
    print(f"Starting web panel on 0.0.0.0:{port}")
    print("Make sure main.py is running first!")
    app.run(host='0.0.0.0', port=port)
