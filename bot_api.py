import requests
import logging
import json
from protobuf_decoder.protobuf_decoder import Parser

def fix_num(number):
    """Clean UID by removing any separators and returning as plain string"""
    return str(number).replace('***', '').strip()

def parse_results(parsed_results):
    """Parse protobuf results into dictionary structure"""
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data["wire_type"] = result.wire_type
        if result.wire_type == "varint":
            field_data["data"] = result.data
        if result.wire_type == "string":
            field_data["data"] = result.data
        if result.wire_type == "bytes":
            field_data["data"] = result.data
        elif result.wire_type == "length_delimited":
            field_data["data"] = parse_results(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def get_available_room(input_text):
    """Parse hex packet data to JSON structure"""
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = parse_results(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        print(f"Error parsing packet: {e}")
        return None

def get_player_status_from_packet(packet):
    """Parse player status from packet data - returns detailed status info"""
    json_result = get_available_room(packet)
    if not json_result:
        return {"status": "OFFLINE"}
    
    parsed_data = json.loads(json_result)

    if "5" not in parsed_data or "data" not in parsed_data["5"]:
        return {"status": "OFFLINE"}

    json_data = parsed_data["5"]["data"]

    if "1" not in json_data or "data" not in json_data["1"]:
        return {"status": "OFFLINE"}

    data = json_data["1"]["data"]

    if "3" not in data:
        return {"status": "OFFLINE"}

    status_data = data["3"]

    if "data" not in status_data:
        return {"status": "OFFLINE"}

    status = status_data["data"]
    result = {}

    if status == 1:
        result["status"] = "SOLO"
    elif status == 2:
        # Player is in squad
        if "9" in data and "data" in data["9"]:
            group_count = data["9"]["data"]
            countmax1 = data["10"]["data"]
            countmax = countmax1 + 1
            result["status"] = f"INSQUAD ({group_count}/{countmax})"
            result["squad_count"] = group_count
            result["squad_max"] = countmax
        else:
            result["status"] = "INSQUAD"
        
        # Get squad leader ID
        if "8" in data and "data" in data["8"]:
            result["squad_leader"] = str(data["8"]["data"])
    
    elif status in [3, 5]:
        result["status"] = "INGAME"
    elif status == 4:
        result["status"] = "IN ROOM"
        # Get room ID
        if "15" in data and "data" in data["15"]:
            result["room_id"] = str(data["15"]["data"])
    elif status in [6, 7]:
        result["status"] = "IN SOCIAL ISLAND MODE"
    else:
        result["status"] = "NOTFOUND"

    return result

def get_nickname_from_api(uid):
    """Get player nickname from API - handles Unicode properly"""
    clean_uid = str(uid).replace('***', '').strip()
    url = f"http://raw.thug4ff.com/info?uid={clean_uid}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Get nickname from nested basicInfo object - JSON automatically handles Unicode
            nickname = data.get('basicInfo', {}).get('nickname', 'Unknown')
            return {
                "status": "success",
                "nickname": nickname,
                "uid": clean_uid
            }
        else:
            return {
                "status": "error",
                "nickname": "Unknown",
                "message": f"Failed to fetch nickname. Status code: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "nickname": "Unknown",
            "message": f"Failed to fetch nickname: {str(e)}"
        }

def check_banned_status(player_id):
    """Check if a player is banned and get their nickname"""
    clean_id = str(player_id).replace('***', '').strip()
    
    # Get nickname first
    nickname_info = get_nickname_from_api(clean_id)
    
    # Get ban status
    ban_url = f"http://amin-team-api.vercel.app/check_banned?player_id={clean_id}"
    try:
        ban_response = requests.get(ban_url, timeout=15)
        if ban_response.status_code == 200:
            ban_data = ban_response.json()
        else:
            ban_data = {"status": "Unknown", "error": "Could not fetch ban status"}
    except Exception as e:
        ban_data = {"status": "Unknown", "error": str(e)}
    
    return {
        "status": "success",
        "data": {
            "ban_status": ban_data.get("status", ban_data.get("Status", "Unknown")),
            "nickname": nickname_info.get("nickname", "Unknown"),
            "uid": clean_id
        }
    }

def get_player_status(uid):
    """Get detailed player status including nickname and squad info"""
    clean_uid = str(uid).replace('***', '').strip()
    
    # Get nickname from API
    nickname_info = get_nickname_from_api(clean_uid)
    nickname = nickname_info.get("nickname", "Unknown")
    
    try:
        # Send status check command to bot with longer timeout to wait for game server response
        response = requests.post(
            'http://127.0.0.1:8080/command',
            json={'action': 'status_check', 'player_id': clean_uid},
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Check if bot returned actual status data
            if 'status_result' in response_data:
                status_result = response_data['status_result']
                game_status = status_result.get('status', 'OFFLINE')
                
                result = {
                    "status": "success",
                    "data": {
                        "uid": clean_uid,
                        "nickname": nickname,
                        "game_status": game_status
                    }
                }
                
                # Add squad leader info if available
                if 'squad_leader' in status_result and status_result['squad_leader']:
                    leader_uid = status_result['squad_leader']
                    leader_info = get_nickname_from_api(leader_uid)
                    result["data"]["squad_leader_uid"] = leader_uid
                    result["data"]["squad_leader_nickname"] = leader_info.get("nickname", "Unknown")
                
                # Add room ID if available
                if 'room_id' in status_result:
                    result["data"]["room_id"] = status_result['room_id']
                
                return result
            else:
                # Check if bot reported auth failure
                if response_data.get('bot_authenticated') == False:
                    return {
                        "status": "error",
                        "data": {
                            "uid": clean_uid,
                            "nickname": nickname,
                            "game_status": "Bot Not Authenticated",
                            "message": "❌ Bot is not authenticated with Free Fire servers. The bot needs valid account credentials to check player status.",
                            "note": "To fix this: Update the bot credentials in main.py (lines 699-700) with a valid Free Fire account UID and password hash."
                        }
                    }
                # Bot command sent but waiting for response
                return {
                    "status": "error",
                    "data": {
                        "uid": clean_uid,
                        "nickname": nickname,
                        "game_status": "No Response",
                        "message": "❌ Status check sent but no response received from game servers after 5 seconds.",
                        "note": "The bot may not be properly connected to Free Fire servers. Check console logs for authentication errors."
                    }
                }
        else:
            return {
                "status": "error",
                "message": f"Bot API returned error: {response.status_code}"
            }
    except Exception as e:
        # Bot not connected, but we can still show nickname
        return {
            "status": "partial",
            "data": {
                "uid": clean_uid,
                "nickname": nickname,
                "game_status": "Bot not connected",
                "message": "❌ Could not connect to bot to check game status, but nickname was retrieved successfully."
            }
        }

def send_invite_two_players(your_uid, target_uid):
    """Send squad invite to two players using bot command queue"""
    clean_your_uid = str(your_uid).replace('***', '').strip()
    clean_target_uid = str(target_uid).replace('***', '').strip()
    
    try:
        response = requests.post(
            'http://127.0.0.1:8080/command',
            json={'action': 'invite_two_players', 'your_uid': clean_your_uid, 'target_uid': clean_target_uid},
            timeout=5
        )
        if response.status_code == 200:
            return {
                "status": "success",
                "message": f"✅ Bot is creating a 5-player squad and sending invites to both {clean_your_uid} and {clean_target_uid}!"
            }
        else:
            return {
                "status": "error",
                "message": f"Bot API returned error: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to communicate with bot: {str(e)}"
        }


def send_spam_requests(uid):
    """Send spam join requests using bot command queue"""
    clean_uid = str(uid).replace('***', '').strip()
    
    try:
        response = requests.post(
            'http://127.0.0.1:8080/command',
            json={'action': 'spam_requests', 'player_id': clean_uid, 'count': 30},
            timeout=5
        )
        if response.status_code == 200:
            return {
                "status": "success",
                "data": {
                    "uid": clean_uid,
                    "message": f"✅ Sending 30 join requests to player {clean_uid}!"
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Bot API returned error: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to communicate with bot: {str(e)}"
        }

def send_spam_invites(uid):
    """Send spam squad invites using bot command queue"""
    clean_uid = str(uid).replace('***', '').strip()
    
    try:
        response = requests.post(
            'http://127.0.0.1:8080/command',
            json={'action': 'spam_invites', 'player_id': clean_uid, 'threads': 29},
            timeout=5
        )
        if response.status_code == 200:
            return {
                "status": "success",
                "data": {
                    "uid": clean_uid,
                    "message": f"✅ Creating 29 threads to spam invites to player {clean_uid}!"
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Bot API returned error: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to communicate with bot: {str(e)}"
        }

def send_team_attack(team_code):
    """Send team join spam attack using bot command queue"""
    if not team_code or len(team_code) < 4:
        return {
            "status": "error",
            "message": "Invalid team code. Please provide a valid team code."
        }
    
    try:
        response = requests.post(
            'http://127.0.0.1:8080/command',
            json={'action': 'team_attack', 'team_code': team_code, 'duration': 45},
            timeout=5
        )
        if response.status_code == 200:
            return {
                "status": "success",
                "data": {
                    "team_code": team_code,
                    "message": f"✅ Team attack started on {team_code} for 45 seconds!"
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Bot API returned error: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to communicate with bot: {str(e)}"
        }
