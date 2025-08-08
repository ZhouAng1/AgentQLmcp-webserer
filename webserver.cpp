#include "webserver.h"

WebServer::WebServer()
{
    //http_conn类对象
    users = new http_conn[MAX_FD];

    //root文件夹路径
    char server_path[200];
    getcwd(server_path, 200);
    char root[6] = "/root";
    m_root = (char *)malloc(strlen(server_path) + strlen(root) + 1);
    strcpy(m_root, server_path);
    strcat(m_root, root);

    //定时器
    users_timer = new client_data[MAX_FD];
}

WebServer::~WebServer()
{
    close(m_epollfd);
    close(m_listenfd);
    close(m_pipefd[1]);
    close(m_pipefd[0]);
    delete[] users;
    delete[] users_timer;
    delete m_pool;
}

void WebServer::init(int port, string user, string passWord, string databaseName, int log_write, 
                     int opt_linger, int trigmode, int sql_num, int thread_num, int close_log, int actor_model)
{
    m_port = port;
    m_user = user;
    m_passWord = passWord;
    m_databaseName = databaseName;
    m_sql_num = sql_num;
    m_thread_num = thread_num;
    m_log_write = log_write;
    m_OPT_LINGER = opt_linger;
    m_TRIGMode = trigmode;
    m_close_log = close_log;
    m_actormodel = actor_model;
}

void WebServer::trig_mode()
{
    //LT + LT
    if (0 == m_TRIGMode)
    {
        m_LISTENTrigmode = 0;
        m_CONNTrigmode = 0;
    }
    //LT + ET
    else if (1 == m_TRIGMode)
    {
        m_LISTENTrigmode = 0;
        m_CONNTrigmode = 1;
    }
    //ET + LT
    else if (2 == m_TRIGMode)
    {
        m_LISTENTrigmode = 1;
        m_CONNTrigmode = 0;
    }
    //ET + ET
    else if (3 == m_TRIGMode)
    {
        m_LISTENTrigmode = 1;
        m_CONNTrigmode = 1;
    }
}

void WebServer::log_write()
{
    if (0 == m_close_log)
    {
        //初始化日志
        if (1 == m_log_write)
            Log::get_instance()->init("./ServerLog", m_close_log, 2000, 800000, 800);
        else
            Log::get_instance()->init("./ServerLog", m_close_log, 2000, 800000, 0);
    }
}

void WebServer::sql_pool()
{
    //初始化数据库连接池
    m_connPool = connection_pool::GetInstance();
    m_connPool->init("localhost", m_user, m_passWord, m_databaseName, 3306, m_sql_num, m_close_log);

    //初始化数据库读取表
    users->initmysql_result(m_connPool);
}

void WebServer::thread_pool()
{
    //线程池
    m_pool = new threadpool<http_conn>(m_actormodel, m_connPool, m_thread_num);
}

void WebServer::eventListen()
{
    //网络编程基础步骤
    m_listenfd = socket(PF_INET, SOCK_STREAM, 0);
    assert(m_listenfd >= 0);

    //优雅关闭连接
    if (0 == m_OPT_LINGER)
    {
        struct linger tmp = {0, 1};
        setsockopt(m_listenfd, SOL_SOCKET, SO_LINGER, &tmp, sizeof(tmp));
    }
    else if (1 == m_OPT_LINGER)
    {
        struct linger tmp = {1, 1};
        setsockopt(m_listenfd, SOL_SOCKET, SO_LINGER, &tmp, sizeof(tmp));
    }
    //设置端口复用
    int reuse = 1;
    //允许一个端口在TIME_WAIT状态下被重新绑定（bind）到新的socket上，而不是说“多个socket同时监听同一个端口”。
    setsockopt(m_listenfd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    //绑定
    int ret = 0;
    struct sockaddr_in address;
    //清空地址结构体    
    bzero(&address, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons(m_port);

    //监听
    ret = bind(m_listenfd, (struct sockaddr *)&address, sizeof(address));
    assert(ret >= 0);
    ret = listen(m_listenfd, 5);
    assert(ret >= 0);

    utils.init(TIMESLOT);

    // 创建epoll事件数组，用于存储epoll_wait返回的事件
    epoll_event events[MAX_EVENT_NUMBER];

    // 创建epoll实例，参数5是内核事件表的大小（已废弃，但必须>0）
    m_epollfd = epoll_create(5);
    assert(m_epollfd != -1);  // 确保创建成功

    // 将监听socket添加到epoll监听列表
    // false表示不设置EPOLLONESHOT，m_LISTENTrigmode是触发模式（LT/ET）
    utils.addfd(m_epollfd, m_listenfd, false, m_LISTENTrigmode);

    // 将epoll文件描述符传递给http连接类，让http连接也能使用epoll
    http_conn::m_epollfd = m_epollfd;

    // 创建管道，用于线程间通信（特别是信号处理）
    // PF_UNIX表示Unix域套接字，SOCK_STREAM表示流式套接字
    // m_pipefd[0]是读端，m_pipefd[1]是写端
    ret = socketpair(PF_UNIX, SOCK_STREAM, 0, m_pipefd);
    assert(ret != -1);  // 确保创建成功

    // 设置管道写端为非阻塞模式
    utils.setnonblocking(m_pipefd[1]);

    // 将管道读端添加到epoll监听列表，用于接收信号通知
    // 0表示LT模式
    utils.addfd(m_epollfd, m_pipefd[0], false, 0);

    // 设置信号处理
    // SIGPIPE信号忽略（客户端断开连接时避免程序退出）
    utils.addsig(SIGPIPE, SIG_IGN);

    // 设置SIGALRM信号处理函数（定时器信号）
    utils.addsig(SIGALRM, utils.sig_handler, false);

    // 设置SIGTERM信号处理函数（终止信号）
    utils.addsig(SIGTERM, utils.sig_handler, false);

    // 启动定时器，TIMESLOT秒后发送SIGALRM信号
    alarm(TIMESLOT);

    //工具类,信号和描述符基础操作
    Utils::u_pipefd = m_pipefd;
    Utils::u_epollfd = m_epollfd;
}

void WebServer::timer(int connfd, struct sockaddr_in client_address)
{
    users[connfd].init(connfd, client_address, m_root, m_CONNTrigmode, m_close_log, m_user, m_passWord, m_databaseName);

    //初始化client_data数据
    //创建定时器，设置回调函数和超时时间，绑定用户数据，将定时器添加到链表中
    users_timer[connfd].address = client_address;
    users_timer[connfd].sockfd = connfd;
    util_timer *timer = new util_timer;
    timer->user_data = &users_timer[connfd];
    timer->cb_func = cb_func;
    time_t cur = time(NULL);
    timer->expire = cur + 3 * TIMESLOT;
    users_timer[connfd].timer = timer;
    utils.m_timer_lst.add_timer(timer);
}

//若有数据传输，则将定时器往后延迟3个单位
//并对新的定时器在链表上的位置进行调整
void WebServer::adjust_timer(util_timer *timer)
{
    time_t cur = time(NULL);
    timer->expire = cur + 3 * TIMESLOT;
    utils.m_timer_lst.adjust_timer(timer);

    LOG_INFO("%s", "adjust timer once");
}
 
void WebServer::deal_timer(util_timer *timer, int sockfd)
{  
    // 调用回调函数处理定时器事件
    timer->cb_func(&users_timer[sockfd]);
    // 如果定时器存在，从链表中删除
    if (timer)
    {
        utils.m_timer_lst.del_timer(timer);
    }

    LOG_INFO("close fd %d", users_timer[sockfd].sockfd);
}

// 处理新客户端连接
bool WebServer::dealclientdata()
{
    struct sockaddr_in client_address; // 客户端地址结构体，存储客户端IP和端口
    socklen_t client_addrlength = sizeof(client_address); // 地址结构体大小，用于accept函数
    if (0 == m_LISTENTrigmode) // LT模式（水平触发）- 0表示LT，1表示ET
    {
        // LT模式：只accept一次，如果没处理完会重复触发epoll事件
        // accept函数：接受新连接，返回新的socket文件描述符
        // (struct sockaddr *)&client_address：强制类型转换，因为accept需要通用地址结构体
        int connfd = accept(m_listenfd, (struct sockaddr *)&client_address, &client_addrlength);
        if (connfd < 0) // accept失败，返回-1
        {
            LOG_ERROR("%s:errno is:%d", "accept error", errno); // 记录错误日志，errno是系统错误码
            return false; // 返回false表示处理失败
        }
        if (http_conn::m_user_count >= MAX_FD) // 检查连接数是否超限，MAX_FD是最大文件描述符数
        {
            utils.show_error(connfd, "Internal server busy"); // 向客户端发送错误信息
            LOG_ERROR("%s", "Internal server busy"); // 记录错误日志
            return false; // 返回false表示处理失败
        }
        timer(connfd, client_address); // 为新连接创建定时器，管理连接超时
    }
    else // ET模式（边缘触发）
    {
        // ET模式：必须一次性处理完所有连接，因为事件只触发一次
        while (1) // 无限循环，直到没有更多连接
        {
            int connfd = accept(m_listenfd, (struct sockaddr *)&client_address, &client_addrlength); // 循环接受新连接
            if (connfd < 0) // accept失败，说明没有更多连接了
            {
                LOG_ERROR("%s:errno is:%d", "accept error", errno); // 记录错误日志
                break; // 跳出循环，没有更多连接了
            }
            if (http_conn::m_user_count >= MAX_FD) // 检查连接数是否超限
            {
                utils.show_error(connfd, "Internal server busy"); // 向客户端发送错误信息
                LOG_ERROR("%s", "Internal server busy"); // 记录错误日志
                break; // 跳出循环，服务器已满
            }
            timer(connfd, client_address); // 为新连接创建定时器
        }
        return false; // ET模式处理完所有连接后返回false
    }
    return true; // LT模式处理成功返回true
}

// 处理信号事件（如定时器超时、服务器终止）
bool WebServer::dealwithsignal(bool &timeout, bool &stop_server)
{
    int ret = 0;
    int sig;
    char signals[1024];
    ret = recv(m_pipefd[0], signals, sizeof(signals), 0); // 从管道读端读取信号
    if (ret == -1)
    {
        return false; // 读取失败
    }
    else if (ret == 0)
    {
        return false; // 没有信号
    }
    else
    {
        for (int i = 0; i < ret; ++i)
        {
            switch (signals[i])
            {
            case SIGALRM: // 定时器信号
            {
                timeout = true; // 设置超时标志
                break;
            }
            case SIGTERM: // 终止信号
            {
                stop_server = true; // 设置停止服务器标志
                break;
            }
            }
        }
    }
    return true;
}

// 处理读事件
void WebServer::dealwithread(int sockfd)
{
    util_timer *timer = users_timer[sockfd].timer; // 获取该连接的定时器

    // reactor模式
    if (1 == m_actormodel)
    {
        if (timer)
        {
            adjust_timer(timer); // 有数据传输，延长定时器超时时间
        }

        m_pool->append(users + sockfd, 0); // 将读任务放入线程池，0表示读

        // 等待线程池处理完成
        while (true)
        {
            if (1 == users[sockfd].improv)
            {
                if (1 == users[sockfd].timer_flag)
                {
                    deal_timer(timer, sockfd); // 处理超时（如关闭连接）
                    users[sockfd].timer_flag = 0;
                }
                users[sockfd].improv = 0;
                break;
            }
        }
    }
    else // proactor模式
    {
        if (users[sockfd].read_once()) // 直接读取数据
        {
            LOG_INFO("deal with the client(%s)", inet_ntoa(users[sockfd].get_address()->sin_addr));
            m_pool->append_p(users + sockfd); // 读成功，放入线程池进一步处理
            if (timer)
            {
                adjust_timer(timer); // 延长定时器超时时间
            }
        }
        else
        {
            deal_timer(timer, sockfd); // 读失败，关闭连接
        }
    }
}

// 处理写事件
void WebServer::dealwithwrite(int sockfd)
{
    util_timer *timer = users_timer[sockfd].timer; // 获取该连接的定时器
    // reactor模式
    if (1 == m_actormodel)
    {
        if (timer)
        {
            adjust_timer(timer); // 有数据传输，延长定时器超时时间
        }

        m_pool->append(users + sockfd, 1); // 将写任务放入线程池，1表示写

        // 等待线程池处理完成
        while (true)
        {
            if (1 == users[sockfd].improv)
            {
                if (1 == users[sockfd].timer_flag)
                {
                    deal_timer(timer, sockfd); // 处理超时（如关闭连接）
                    users[sockfd].timer_flag = 0;
                }
                users[sockfd].improv = 0;
                break;
            }
        }
    }
    else // proactor模式
    {
        if (users[sockfd].write()) // 直接写数据
        {
            LOG_INFO("send data to the client(%s)", inet_ntoa(users[sockfd].get_address()->sin_addr));
            if (timer)
            {
                adjust_timer(timer); // 延长定时器超时时间
            }
        }
        else
        {
            deal_timer(timer, sockfd); // 写失败，关闭连接
        }
    }
}

void WebServer::eventLoop()
{    
    //初始化 二者初始都关闭
    bool timeout = false;
    bool stop_server = false;
     //循环处理事件
    while (!stop_server)
    {   //等待事件发生  epoll_wait函数会阻塞，直到有事件发生
        int number = epoll_wait(m_epollfd, events, MAX_EVENT_NUMBER, -1);
        if (number < 0 && errno != EINTR)
        {
            LOG_ERROR("%s", "epoll failure");
            break;
        }
        //遍历所有事件
        for (int i = 0; i < number; i++)
        {     
            //获取事件的文件描述符  
            int sockfd = events[i].data.fd;

            //处理新到的客户连接
            if (sockfd == m_listenfd)
            {
                // 1. 监听socket有事件，说明有新客户端要连接
                // 处理新连接（accept），分配资源
                bool flag = dealclientdata();
                if (false == flag)
                    continue; // 处理失败，跳过本次事件
            }
            else if (events[i].events & (EPOLLRDHUP | EPOLLHUP | EPOLLERR))
            {
                // 2. 连接异常事件
                // EPOLLRDHUP：对端关闭连接
                // EPOLLHUP：连接挂起
                // EPOLLERR：连接出错
                // 处理方式：关闭连接，移除定时器
                util_timer *timer = users_timer[sockfd].timer;
                deal_timer(timer, sockfd);
            }
            //处理信号
            else if ((sockfd == m_pipefd[0]) && (events[i].events & EPOLLIN))
            {
                // 3. 信号事件
                // sockfd等于管道读端，且有可读事件，说明有信号（如定时器超时、服务器终止）到来
                // 处理信号，设置timeout/stop_server标志
                bool flag = dealwithsignal(timeout, stop_server);
                if (false == flag)
                    LOG_ERROR("%s", "dealclientdata failure");
            }
            //处理客户连接上接收到的数据
            else if (events[i].events & EPOLLIN)
            {
                // 4. 客户端socket有可读事件
                // 客户端发来数据，处理读操作
                dealwithread(sockfd);
            }
            else if (events[i].events & EPOLLOUT)
            {
                // 5. 客户端socket有可写事件
                // 服务器有数据要发给客户端，处理写操作
                dealwithwrite(sockfd);
            }
        }
        if (timeout)
        {
            utils.timer_handler();

            LOG_INFO("%s", "timer tick");

            timeout = false;
        }
    }
}
