$(document).ready(function () {
    let currentUser = null;
    const apiUrl = "http://127.0.0.1:5000";  // Flask 伺服器網址
    const socket = io(apiUrl);

    // 切換使用者
    $(".user-btn").click(function () {
        currentUser = $(this).data("user");
        $(".user-btn").removeClass("active");
        $(this).addClass("active");
    });

    // 建立 10x4 格子
    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 4; col++) {
            $("#grid-container").append(`<div class="cell" data-row="${row}" data-col="${col}"></div>`);
        }
    }

    // 點選格子
    $(".cell").click(function () {
        if (!currentUser) {
            alert("請先選擇使用者！");
            return;
        }

        let row = $(this).data("row");
        let col = $(this).data("col");

        $.ajax({
            url: apiUrl + "/select",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ user_id: currentUser, row: row, col: col }),
            error: function (xhr) {
                alert(xhr.responseJSON.error);
            }
        });
    });

    // 清除按鈕
    $("#clear-btn").click(function () {
        $.post(apiUrl + "/clear", function () {
            updateGrid([[null, null, null, null]]);
        });
    });

    // 更新格子顏色
    function updateGrid(grid) {
        $(".cell").each(function () {
            let row = $(this).data("row");
            let col = $(this).data("col");
            let color = grid[row][col];

            if (color) {
                $(this).css("background-color", color).addClass("selected");
            } else {
                $(this).css("background-color", "white").removeClass("selected");
            }
        });
    }

    // 透過 WebSocket 實時更新
    socket.on("update_grid", function (data) {
        updateGrid(data);
    });

    // 初始載入格子
    $.get(apiUrl + "/get-grid", function (data) {
        updateGrid(data);
    });
});
