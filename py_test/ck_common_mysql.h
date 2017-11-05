#ifndef CK_COMMON_MYSQL_H__
#define CK_COMMON_MYSQL_H__

#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct mysql_connection_s {
    const char *username;   //用户名
    const char *password;   //密码
    const char *host;       //地址
    int         port;       //端口
    const char *dbname;     //数据库名称
    const char *socket;     //数据库名称
} mysql_connection_t;

typedef int (*fetch_callback)(void *param, int ncols, char **row,
                              unsigned long *lengths);
/**
* @func    初始化myslq
* @argc    创建连接mysql数据结构
* @return  0:成功,其他值创建失败
 */
int ck_mysql_init(const mysql_connection_t *uri);
/**
* @func    执行sql语句
* @argc    sql语句,sql长度,执行结果
* @return  0:成功,其他值创建失败
 */
int ck_mysql_exec(const char *sql, size_t len, void **result);
/**
* @func    批量执行sql insert语句
* @argc    sql语句,sql长度,执行结果
* @return  0:成功,其他值创建失败
 */
int ck_mysql_exec_batch(const char *sql, size_t len, void **outp);

/**
* @func    执行sql语句
* @argc    sql语句,sql长度,回调函数,回调参数
* @return  0:成功,其他值创建失败
 */
int ck_mysql_exec_ex(const char *sql, size_t len,
                   fetch_callback callback,  // Callback function
                   void *data);              // 1st argument to callback

/**
* @func    特殊字符串转换
* @argc    传入字符串,字符串长度,转换后字符串
* @return  转换后字符串长度
 */
size_t ck_mysql_escape_string(const char *from, size_t len, char *to);
/**
* @func    关闭连接
* @argc
* @return
 */
void ck_mysql_close();

/**
* @func    读取配置文件
* @argc    文件名
* @return  文件内容
 */
char *ck_mysql_read_file(const char *filename, long *size);

/**
* @func    解析配置文件
* @argc    mysql连接的结构
* @return
 */
int ck_mysql_parse_conf(mysql_connection_t *tokengen_uri);
int ck_mysql_parse_conf_ex(mysql_connection_t *tokengen_uri);
#ifdef __cplusplus
}
#endif

#endif
