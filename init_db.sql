-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS test;

-- 使用数据库
USE test;

-- 创建用户表
CREATE TABLE IF NOT EXISTS user (
    username VARCHAR(50) PRIMARY KEY,
    passwd VARCHAR(50) NOT NULL
);

-- 插入测试用户
INSERT IGNORE INTO user (username, passwd) VALUES ('test', 'test'); 