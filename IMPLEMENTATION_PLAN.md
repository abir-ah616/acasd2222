# MultifuncionalBot Features Integration Plan

## Current Status (2025-11-18)
The Free Fire bot has a web panel (working) but the advanced features (status, invite, spam, attack) are NOT working because the packet logic from MultifuncionalBot/app.py has not been ported to main.py's async architecture.

## Problem
- Web panel calls bot_api.py functions
- bot_api.py uses external API (https://info-murex.vercel.app/) which is DOWN
- Features need to send ACTUAL game packets via the bot's TCP connection
- Packet creation functions are in MultifuncionalBot (sync) but main.py uses async/await

## Solution: Port Packet Logic

### Step 1: Port Helper Functions from MultifuncionalBot to main.py
From `MultifuncionalBot/app.py` and `MultifuncionalBot/byte.py`:
- `fix_num(num)` - Formats numbers with [c] separators
- `get_random_avatar()` - Returns random avatar ID
- `get_player_status(packet)` - Parses player status from packet response
- `create_protobuf_packet(fields)` - Creates protobuf packets (from byte.py)
- `encrypt_packet(plain_text, key, iv)` - Encrypts packets with AES
- `dec_to_hex(ask)` - Converts decimal to hex
- `join_teamcode(inv, room_id, key, iv)` - Joins team via code (from byte.py)

### Step 2: Port Packet Creation Functions to main.py
These create the actual game packets (all from MultifuncionalBot/app.py class methods):
- `nmnmmmmn(data, key, iv)` - AES encryption helper
- `createpacketinfo(player_id)` - Request player status (0515 header)
- `request_skwad(player_id)` - Send join request (0515 header)
- `invite_skwad(player_id)` - Send squad invite (0515 header)
- `skwad_maker()` - Create new squad (0515 header)
- `changes(num)` - Change squad size 1-6 (0515 header)
- `leave_s()` - Leave current squad (0515 header)
- `start_autooo()` - Auto-start game packet (0515 header)

### Step 3: Update main.py command_processor()
Add new command handlers:
- `"status_check"` - Send createpacketinfo() packet, wait for 0f00 response, parse with get_player_status()
- `"spam_requests"` - Loop 30 times sending request_skwad() packets
- `"spam_invites"` - Create 29 async tasks, each: skwad_maker() → changes(5) → invite_skwad() → sleep(4) → leave_s() → changes(1)
- `"team_attack"` - Loop for 45 seconds: join_teamcode() → start_autooo() → leave_s() → sleep(0.15)
- `"invite_two_players"` - Create squad, invite target AND sender, both get invites

### Step 4: Update bot_api.py
Replace external API calls with bot command queue:
```python
async def process_status(uid):
    await bot_state["command_queue"].put({"action": "status_check", "player_id": uid})
    # Wait for response or return "Command queued"
    
async def process_sm(uid):
    await bot_state["command_queue"].put({"action": "spam_requests", "player_id": uid, "count": 30})
```

### Step 5: Update templates/invite.html
Add second UID input field:
```html
<input type="text" id="your_uid" name="your_uid" placeholder="Your Player UID" required>
<input type="text" id="target_uid" name="target_uid" placeholder="Target Player UID" required>
```
Bot will create 5-player squad and invite BOTH players.

### Step 6: Test Features
- Test with valid bot credentials (not rate-limited)
- Verify packets are sent via online_writer
- Check console logs for errors
- Test each feature individually

## Technical Notes

### Packet Structure
All packets follow this format:
```
[HEADER][LENGTH][ENCRYPTED_PAYLOAD]
- HEADER: 0515 (online), 0E15 (chat), 1200 (received)
- LENGTH: Hex length of encrypted payload (2-5 chars with leading zeros)
- ENCRYPTED_PAYLOAD: AES-CBC encrypted protobuf packet
```

### Key Dependencies
- Protobuf fields dict → create_protobuf_packet() → encrypt with AES → add header/length
- Bot needs valid key, iv from authentication
- Online_writer must be connected

### Async Conversion
MultifuncionalBot uses sync sockets, main.py uses async. Convert:
- `socket.send(packet)` → `await SEndPacKeT(online_writer, None, 'OnLine', packet)`
- `sleep(1)` → `await asyncio.sleep(1)`
- Threading → asyncio.create_task()

## Files to Modify
1. main.py - Add packet functions + command handlers
2. bot_api.py - Replace API calls with command queue
3. templates/invite.html - Add second UID field
4. web_panel.py - Update /api/invite endpoint

## Expected Behavior After Implementation
- Status Check: Sends packet → receives 0f00 response → displays "SOLO/INSQUAD/INGAME/IN ROOM"
- Invite: Creates 5-player squad → invites target + sender → both receive in-game invite
- SM: Sends 30 join requests rapidly → target gets spam
- X: Creates 29 threads → each spams 6-player squad invites → massive spam
- Attack: Joins team code → leaves → joins → leaves for 45 seconds → disrupts lobby
