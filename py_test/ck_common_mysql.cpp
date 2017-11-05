#include <stdlib.h>
#include <errno.h>
#include <mysql.h>
#include <json-c/json.h>
#include <sys/time.h>
#include "ck_common_mysql.h"

#ifdef __cplusplus
extern "C" {
#endif
#include "iniparser.h"

int ck_mysql_init_ex(const mysql_connection_t *uri, void **hp)
{
    unsigned int timeout;
    unsigned long options;
    my_bool reconnect = 1;
    MYSQL *handler, *pmysql;

    if (uri == NULL || hp == NULL) {
        return EINVAL;
    }

    *hp = NULL;
    pmysql = (MYSQL *)calloc(1, sizeof(MYSQL));
    if ((handler = mysql_init(pmysql)) == NULL) {
        return EFAULT;
    }

    mysql_options(handler, MYSQL_OPT_RECONNECT, &reconnect);

    timeout = 5;
    mysql_options(handler, MYSQL_OPT_READ_TIMEOUT, (char *)&timeout);
    mysql_options(handler, MYSQL_OPT_WRITE_TIMEOUT, (char *)&timeout);
    mysql_options(handler, MYSQL_SET_CHARSET_NAME, "utf8");


    options = CLIENT_MULTI_RESULTS|CLIENT_MULTI_STATEMENTS;

    handler = mysql_real_connect(pmysql,
                                 uri->host,
                                 uri->username,
                                 uri->password,
                                 uri->dbname,
                                 uri->port,
                                 uri->socket,
                                 options);
    if (handler == NULL) {
        printf("connect failure: %s\n", mysql_error(pmysql));
        return EINVAL;

        mysql_close(pmysql);
    }

    *hp = pmysql;
    return 0;
}

static MYSQL *mysql_handle = NULL;
int ck_mysql_init(const mysql_connection_t *uri)
{
    if (mysql_handle) {
        mysql_close(mysql_handle);
        free(mysql_handle);
    }

    return ck_mysql_init_ex(uri, (void **)&mysql_handle);
}

int ck_mysql_exec_batch(const char *sql, size_t len, void **outp)
{
    struct timeval start,end;
    gettimeofday(&start,NULL);
    int rc;
    MYSQL_RES *result;

    if (outp) {
        *outp = NULL;
    }

    rc = mysql_real_query(mysql_handle, sql, len);
    if (rc) {
        printf("%s() execute sql '%s' error: %s\n", __FUNCTION__, sql,
               mysql_error(mysql_handle));
        return EIO;
    }

    if (outp) {
        result = mysql_store_result(mysql_handle);
        if (result == NULL) {
            printf("%s() sql '%s' return NULL result error: %s\n", __FUNCTION__, sql,
                   mysql_error(mysql_handle));
            return EIO;
        }
        *outp = result;
    }
    do
    {
        result = mysql_store_result( mysql_handle);
        mysql_free_result(result);
    }while( !mysql_next_result( mysql_handle ) );
    gettimeofday(&end,NULL);
    //int timeuse = 1000000*( end.tv_sec - start.tv_sec ) + end.tv_usec - start.tv_usec;
    //printf("mysql exec time:%d us,sql=%s\n",timeuse,sql);

    return rc;
}
int ck_mysql_exec(const char *sql, size_t len, void **outp)
{
    struct timeval start,end;
    gettimeofday(&start,NULL);
    int rc;
    MYSQL_RES *result;

    if (outp) {
        *outp = NULL;
    }

    rc = mysql_real_query(mysql_handle, sql, len);
    if (rc) {
        printf("%s() execute sql '%s' error: %s\n", __FUNCTION__, sql,
               mysql_error(mysql_handle));
        return EIO;
    }

    if (outp) {
        result = mysql_store_result(mysql_handle);
        if (result == NULL) {
            printf("%s() sql '%s' return NULL result error: %s\n", __FUNCTION__, sql,
                   mysql_error(mysql_handle));
            return EIO;
        }
        *outp = result;
    }
    gettimeofday(&end,NULL);
    //int timeuse = 1000000*( end.tv_sec - start.tv_sec ) + end.tv_usec - start.tv_usec;
    //printf("mysql exec time:%d us,sql=%s\n",timeuse,sql);

    return rc;
}

int ck_mysql_exec_ex(const char *sql, size_t len, fetch_callback callback,
                   void *data)
{
    int rc;
    unsigned long     *lengths;
    MYSQL_ROW          row;
    MYSQL_RES         *result;


    result = NULL;
    rc = mysql_real_query(mysql_handle, sql, len);
    if (rc) {
        printf("%s() execute sql '%s' error: %s\n", __FUNCTION__, sql,
               mysql_error(mysql_handle));
        return EIO;
    }

    if (!callback) { // No need to fetch data
        if (mysql_field_count(mysql_handle)) {
            printf("Warning: It was a select statement, but no callback supplied\n");
            result = mysql_use_result(mysql_handle);
            if (result) {
                mysql_free_result(result);
            }
        }

        return 0;
    }

    result = mysql_use_result(mysql_handle);
    if (result == NULL) {
        printf("%s() sql '%s' return NULL result error: %s\n", __FUNCTION__, sql,
               mysql_error(mysql_handle));
        return EIO;
    }

    while ((row = mysql_fetch_row(result)) != NULL) {
        lengths = mysql_fetch_lengths(result);
        rc = callback(data, mysql_num_fields(result), row, lengths);
        if (rc) {
            break;
        }
    }

    // fetch remaining rows
    /**
     *  When using mysql_use_result(), you must execute mysql_fetch_row()
     *  until a NULL value is returned, otherwise, the unfetched rows are
     *  returned as part of the result set for your next query. The C API
     *  gives the error Commands out of sync; you can't run this command
     *  now if you forget to do this!
     */

    if (row != NULL) {
        printf("Warning: Callback function aborted, rows still remaining\n");
        while ((row = mysql_fetch_row(result)) != NULL)
            ;
    }
    if (result) {
        mysql_free_result(result);
    }

    return 0;
}

size_t ck_mysql_escape_string(const char *from, size_t len, char *to)
{
    return mysql_real_escape_string(mysql_handle, to, from, len);
}

void ck_mysql_close()
{
    if (mysql_handle) {
        mysql_close(mysql_handle);
        free(mysql_handle);
        mysql_handle = NULL;
    }
}

char *ck_mysql_read_file(const char *filename, long *size)
{
    FILE *f = fopen(filename, "rb");
    char *string = NULL;
    if (f == NULL)
    {
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    // hand back size of file
    *size = fsize;
    string = (char *)malloc(fsize + 1);
    if (string == NULL)
    {
        return NULL;
    }
    fread(string, fsize, 1, f);
    fclose(f);
    string[fsize] = 0;
    return string;
}

int ck_mysql_parse_conf_ex(mysql_connection_t *tokengen_uri)
{
    dictionary *ini;
    char *str_ini;
    ini = iniparser_load("/etc/my.cnf");//parser the file
    if(ini == NULL)
    {
        return -1;
    }
    tokengen_uri->host = "127.0.0.1";
    tokengen_uri->dbname = "cloudkeeper";
    str_ini = iniparser_getstring(ini,"mysqld_multi:user",NULL);
    if(str_ini)
    {
        tokengen_uri->username = str_ini;
    }
    str_ini = iniparser_getstring(ini,"mysqld_multi:password",NULL);
    if(str_ini)
    {
        tokengen_uri->password = str_ini;
    }

    str_ini = iniparser_getstring(ini,"mysqld1:port",NULL);
    if(str_ini)
    {
        tokengen_uri->port = atoi(str_ini);
    }
    str_ini = iniparser_getstring(ini,"mysqld1:socket",NULL);
    if(str_ini)
    {
        tokengen_uri->socket = str_ini;
    }
    iniparser_freedict(ini);//free dirctionary obj
    return 0;
}

int ck_mysql_parse_conf(mysql_connection_t *tokengen_uri)
{
    long config_size;
    char * json = ck_mysql_read_file("/csg/config/mysql_conf.json",&config_size);
    struct json_object *new_obj,*option_obj,*tmp_obj;
    if(json == NULL)
    {
        return -1;
    }
    new_obj = json_tokener_parse(json);
    if(new_obj == NULL)
    {
        return -1;
    }
    bool ret = json_object_object_get_ex(new_obj, "mysql_connect_master",&option_obj);
    if(!ret)
    {
        return -1;
    }

    ret = json_object_object_get_ex(option_obj, "host",&tmp_obj);
    if(!ret)
    {
        return -1;
    }
    tokengen_uri->host = json_object_get_string(tmp_obj);

    ret = json_object_object_get_ex(option_obj, "username",&tmp_obj);
    if(!ret)
    {
        return -1;
    }
    tokengen_uri->username = json_object_get_string(tmp_obj);
    ret = json_object_object_get_ex(option_obj, "password",&tmp_obj);
    if(!ret)
    {
        return -1;
    }
    tokengen_uri->password = json_object_get_string(tmp_obj);
    ret = json_object_object_get_ex(option_obj, "port",&tmp_obj);
    if(!ret)
    {
        return -1;
    }
    tokengen_uri->port = json_object_get_int(tmp_obj);
    ret = json_object_object_get_ex(option_obj, "dbname",&tmp_obj);
    if(!ret)
    {
        return -1;
    }
    tokengen_uri->dbname = json_object_get_string(tmp_obj);
    ret = json_object_object_get_ex(option_obj, "socket",&tmp_obj);
    if(!ret)
    {
        return -1;
    }
    tokengen_uri->socket = json_object_get_string(tmp_obj);
    return 0;
}
#ifdef __cplusplus
}
#endif
