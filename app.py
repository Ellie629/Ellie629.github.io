from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 房間資料結構 (每個房間的格子狀態)
rooms = {}

# 定義 4 種顏色 (每位使用者對應一個)
user_colors = ["red", "blue", "green", "yellow"]

def generate_room_code():
    """產生隨機 6 碼房間碼"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route("/create-room", methods=["POST"])
def create_room():
    """建立新房間"""
    room_code = generate_room_code()
    rooms[room_code] = [[None for _ in range(4)] for _ in range(10)]  # 10x4 空格
    return jsonify({"room_code": room_code})

@app.route("/get-grid/<room_code>", methods=["GET"])
def get_grid(room_code):
    """取得房間內的格子狀態"""
    if room_code in rooms:
        return jsonify(rooms[room_code])
    return jsonify({"error": "房間不存在"}), 404

@app.route("/select", methods=["POST"])
def select_cell():
    """使用者選擇格子"""
    data = request.json
    room_code = data.get("room_code")
    user_id = int(data.get("user_id"))
    row = data.get("row")
    col = data.get("col")

    if room_code not in rooms:
        return jsonify({"error": "房間不存在"}), 400
    if user_id < 1 or user_id > 4:
        return jsonify({"error": "無效的使用者"}), 400

    color = user_colors[user_id - 1]  # 取得對應顏色

    # 確保該使用者在該行內只能選擇一個格子
    if any(rooms[room_code][row][c] == color for c in range(4)):
        return jsonify({"error": "你已經在這一行選擇過格子了！"}), 400

    # 設定格子顏色
    rooms[room_code][row][col] = color

    # 廣播更新給房間內所有人
    socketio.emit("update_grid", rooms[room_code], room=room_code)

    return jsonify({"message": "格子選擇成功", "grid": rooms[room_code]})

@app.route("/clear/<room_code>", methods=["POST"])
def clear_grid(room_code):
    """清除房間內所有格子"""
    if room_code in rooms:
        rooms[room_code] = [[None for _ in range(4)] for _ in range(10)]
        socketio.emit("update_grid", rooms[room_code], room=room_code)
        return jsonify({"message": "格子已清除"})
    return jsonify({"error": "房間不存在"}), 400

@socketio.on("join")
def handle_join(data):
    """使用者加入房間"""
    room_code = data["room_code"]
    join_room(room_code)
    emit("update_grid", rooms.get(room_code, [[None for _ in range(4)] for _ in range(10)]), room=room_code)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
