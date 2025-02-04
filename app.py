from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import random
import string

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}  # 存放房間資訊
user_colors = ["red", "blue", "green", "yellow"]  # 可選擇的顏色


def generate_room_code():
    """產生隨機 10 碼房間碼（大小寫+數字）"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))


@app.route("/")
def home():
    """首頁 - RJPQ 工具"""
    return render_template("index.html")


@app.route("/create-room", methods=["GET", "POST"])
def create_room():
    """創建房間頁面"""
    if request.method == "POST":
        room_code = generate_room_code()
        password = request.form["password"]
        rooms[room_code] = {
            "password": password,
            "grid": [[None for _ in range(4)] for _ in range(10)],
            "users": {}  # 存放加入的使用者
        }
        return render_template("room.html", room_code=room_code, colors=user_colors)
    return render_template("create_room.html")

@app.route('/example', methods=['GET', 'POST'])
def example():
    if request.method == 'POST':
        return "Received POST request"
    return "Received GET request"



@app.route("/join-room", methods=["POST"])
def join_room_api():
    """使用者輸入房間碼後加入房間"""
    data = request.json
    room_code = data.get("room_code")
    if room_code in rooms:
        return jsonify({"success": True})
    return jsonify({"error": "房間不存在"}), 404


@app.route("/room/<room_code>")
def room(room_code):
    """秘密小房間頁面"""
    if room_code not in rooms:
        return "房間不存在", 404
    return render_template("room.html", room_code=room_code, colors=user_colors)


@socketio.on("join")
def handle_join(data):
    """使用者加入 WebSocket 房間"""
    room_code = data["room_code"]
    join_room(room_code)
    emit("update_grid", rooms[room_code]["grid"], room=room_code)


@socketio.on("select_cell")
def handle_select_cell(data):
    """處理使用者選擇格子"""
    room_code = data["room_code"]
    row, col, color = data["row"], data["col"], data["color"]

    if room_code not in rooms:
        return

    # 確保該行只允許一個顏色
    if any(rooms[room_code]["grid"][row][c] == color for c in range(4)):
        return

    rooms[room_code]["grid"][row][col] = color
    emit("update_grid", rooms[room_code]["grid"], room=room_code)


@socketio.on("clear_grid")
def handle_clear_grid(data):
    """清除所有格子"""
    room_code = data["room_code"]
    rooms[room_code]["grid"] = [[None for _ in range(4)] for _ in range(10)]
    emit("update_grid", rooms[room_code]["grid"], room=room_code)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
