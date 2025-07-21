#!/bin/sh

# 根据环境变量设置代理
if [ -n "$SOCKS5_PROXY" ]; then
    export ALL_PROXY="socks5://$SOCKS5_PROXY"
fi

if [ -n "$HTTP_PROXY" ]; then
    export HTTP_PROXY="$HTTP_PROXY"
fi

if [ -n "$HTTPS_PROXY" ]; then
    export HTTPS_PROXY="$HTTPS_PROXY"
fi

# 执行主程序
exec /app/tgs "$@"
    
