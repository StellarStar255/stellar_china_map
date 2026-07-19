#!/bin/bash
# 双击启动本地服务器并打开浏览器。
# 端口被旧的地图服务器占用时自动结束并释放；被其他程序占用时自动顺延端口。
cd "$(dirname "$0")"

PORT=8471
PIDS=$(lsof -nP -tiTCP:$PORT -sTCP:LISTEN)
if [ -n "$PIDS" ]; then
  # 判断占用者是否本站服务器：页面标题匹配，或进程本身是 python http.server
  IS_OURS=""
  curl -s --max-time 1 "http://localhost:$PORT" | grep -q "山河舆图" && IS_OURS=1
  if [ -z "$IS_OURS" ]; then
    for p in $PIDS; do
      ps -o command= -p "$p" | grep -q "http.server" && IS_OURS=1
    done
  fi
  if [ -n "$IS_OURS" ]; then
    echo "端口 $PORT 被旧的地图服务器占用，自动释放中…"
    kill $PIDS 2>/dev/null
    sleep 1
    for p in $PIDS; do kill -0 "$p" 2>/dev/null && kill -9 "$p" 2>/dev/null; done
    sleep 0.5
  fi
  # 仍被占用（说明是其他程序）→ 顺延找空闲端口
  while lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; do
    PORT=$((PORT+1))
  done
  [ "$PORT" != "8471" ] && echo "端口 8471 被其他程序占用，改用 $PORT"
fi

echo "山河舆图 · 本地服务器"
echo "浏览器访问: http://localhost:$PORT  (按 Ctrl+C 停止)"
( sleep 1; open "http://localhost:$PORT" ) &
exec python3 -m http.server "$PORT" --bind 127.0.0.1
