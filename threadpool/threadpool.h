#ifndef THREADPOOL_H
#define THREADPOOL_H

#include <list>
#include <cstdio>
#include <exception>
#include <pthread.h>
#include "../lock/locker.h"
#include "../CGImysql/sql_connection_pool.h"

template <typename T>
class threadpool
{
public:
    /*thread_number是线程池中线程的数量，max_requests是请求队列中最多允许的、等待处理的请求的数量*/
    //actor_model是模型切换，0表示reactor，1表示proactor
    //connPool是数据库连接池指针
    //thread_number是线程池中线程的数量
    //max_request是请求队列中最多允许的、等待处理的请求的数量
    threadpool(int actor_model, connection_pool *connPool, int thread_number = 8, int max_request = 10000);
    ~threadpool();
    //append是添加任务到请求队列中
    //append_p是添加任务到请求队列中，不设置状态
    bool append(T *request, int state);
    bool append_p(T *request);

private:
    /*工作线程运行的函数，它不断从工作队列中取出任务并执行之*/
    static void *worker(void *arg);
    //run是工作线程运行的函数，它不断从工作队列中取出任务并执行之
    void run();

private:
    int m_thread_number;        //线程池中的线程数
    int m_max_requests;         //请求队列中允许的最大请求数
    pthread_t *m_threads;       //描述线程池的数组，其大小为m_thread_number
    std::list<T *> m_workqueue; //请求队列
    locker m_queuelocker;       //保护请求队列的互斥锁
    sem m_queuestat;            //是否有任务需要处理
    connection_pool *m_connPool;  //数据库
    int m_actor_model;          //模型切换
};   
  /*
  
  */    
  //构造函数
template <typename T>

threadpool<T>::threadpool( int actor_model, connection_pool *connPool, int thread_number, int max_requests) : m_actor_model(actor_model),m_thread_number(thread_number), m_max_requests(max_requests), m_threads(NULL),m_connPool(connPool)
{   
    //如果线程数或请求数小于等于0，抛出异常
    if (thread_number <= 0 || max_requests <= 0)
        throw std::exception();
    //创建线程数组
    m_threads = new pthread_t[m_thread_number];
    //如果线程数组创建失败，抛出异常
    if (!m_threads)
        throw std::exception();
    //创建线程
    for (int i = 0; i < thread_number; ++i)
    {
        //创建线程
        if (pthread_create(m_threads + i, NULL, worker, this) != 0)
        {
            //删除线程数组
            delete[] m_threads;
            throw std::exception();
        }
        //分离线程
        if (pthread_detach(m_threads[i]))
        {
            //删除线程数组
            delete[] m_threads;
            throw std::exception();
        }
    }
}
//析构函数
template <typename T>
threadpool<T>::~threadpool()
{
    delete[] m_threads;
}
//添加任务到请求队列中
template <typename T>
bool threadpool<T>::append(T *request, int state)
{
    //加锁
    m_queuelocker.lock();
    //如果请求队列中的请求数大于等于最大请求数，解锁并返回false
    if (m_workqueue.size() >= m_max_requests)
    {
        m_queuelocker.unlock();
        return false;
    }
    //设置请求状态
    request->m_state = state;
    //将请求添加到请求队列中
    m_workqueue.push_back(request);
    //解锁
    m_queuelocker.unlock();
    //增加信号量
    m_queuestat.post();
    return true;
}
template <typename T>
//添加任务到请求队列中，不设置状态
bool threadpool<T>::append_p(T *request)
{
    //加锁
    m_queuelocker.lock();
    //如果请求队列中的请求数大于等于最大请求数，解锁并返回false
    if (m_workqueue.size() >= m_max_requests)
    {
        m_queuelocker.unlock();
        return false;
    }
    //将请求添加到请求队列中
    m_workqueue.push_back(request);
    //解锁
    m_queuelocker.unlock();
    //增加信号量
    m_queuestat.post();
    return true;
}
//工作线程运行的函数
template <typename T>
void *threadpool<T>::worker(void *arg)
{   
    //获取线程池指针
    threadpool *pool = (threadpool *)arg;
    //运行线程池
    pool->run();
    //返回线程池指针
    return pool;
}
//工作线程运行的函数
template <typename T>
void threadpool<T>::run()
{   
    //循环
    while (true)
    {
        //等待信号量
        m_queuestat.wait();
        //加锁
        m_queuelocker.lock();
        //如果请求队列为空，解锁并继续
        if (m_workqueue.empty())
        {
            m_queuelocker.unlock();
            continue;
        }
        //获取请求
        T *request = m_workqueue.front();
        //删除请求
        m_workqueue.pop_front();
        //解锁
        m_queuelocker.unlock();
        //如果请求为空，继续
        if (!request)
            continue;
        //如果模型为proactor，执行
        if (1 == m_actor_model)
        {
            //如果请求状态为0，执行
            if (0 == request->m_state)
            {
                //如果读取请求成功，执行
                if (request->read_once())
                {
                    //设置请求状态
                    request->improv = 1;
                    //获取数据库连接
                    connectionRAII mysqlcon(&request->mysql, m_connPool);
                    //处理请求
                    request->process();
                }
                else
                {
                    //设置请求状态
                    request->improv = 1;
                    request->timer_flag = 1;
                }
            }
            else
            {
                //如果写入请求成功，执行
                if (request->write())
                {
                    //设置请求状态
                    request->improv = 1;
                }
                else
                {
                    //设置请求状态
                    request->improv = 1;
                    request->timer_flag = 1;
                }
            }
            }
        //如果模型为reactor，执行
        else
        {
            //获取数据库连接
            connectionRAII mysqlcon(&request->mysql, m_connPool);
            //处理请求
            request->process();
        }
    }
}
#endif
