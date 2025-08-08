CXX ?= g++

DEBUG ?= 1
ifeq ($(DEBUG), 1)
    CXXFLAGS += -g
else
    CXXFLAGS += -O2

endif

server: main.cpp timer/lst_timer.cpp http/http_conn.cpp log/log.cpp webserver.cpp config.cpp
	g++ -o server main.cpp timer/lst_timer.cpp http/http_conn.cpp log/log.cpp webserver.cpp config.cpp -g -lpthread

# 如果需要数据库功能，使用下面的命令
# server_with_db: main.cpp timer/lst_timer.cpp http/http_conn.cpp log/log.cpp CGImysql/sql_connection_pool.cpp webserver.cpp config.cpp
# 	g++ -o server main.cpp timer/lst_timer.cpp http/http_conn.cpp log/log.cpp CGImysql/sql_connection_pool.cpp webserver.cpp config.cpp -g -lpthread -lmysqlclient

clean:
	rm  -r server
