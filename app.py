from flask import Flask, jsonify, request
from flask_cors import CORS # type: ignore

app = Flask(__name__)
CORS(app)  # 允許跨來源請求

# 初始化 10x4 格子，每個格子初始為空
grid = [[None for _ in range(4)] for _ in range(10)]

# 定義使用者顏色
user_colors = {
    "1": "red",
    "2": "blue",
    "3": "green",
    "4": "yellow"
}

@app.route("/get-grid", methods=["GET"])
def get_grid():
    """取得當前的格子狀態"""
    return jsonify(grid)

@app.route("/select", methods=["POST"])
def select_cell():
    """使用者選擇格子"""
    data = request.json
    user_id = str(data.get("user_id"))  # 轉為字串以符合 user_colors
    row = data.get("row")
    col = data.get("col")

    if user_id not in user_colors:
        return jsonify({"error": "無效的使用者"}), 400

    # 確保行號與列號有效
    if row < 0 or row >= 10 or col < 0 or col >= 4:
        return jsonify({"error": "無效的格子"}), 400

    # 確保同一使用者在該行只能選一格
    if any(grid[row][c] == user_colors[user_id] for c in range(4)):
        return jsonify({"error": "你已經在這一行選擇過格子了！"}), 400

    # 設置格子的顏色
    grid[row][col] = user_colors[user_id]
    return jsonify({"message": "格子選擇成功", "grid": grid})

if __name__ == "__main__":
    app.run(debug=True)
