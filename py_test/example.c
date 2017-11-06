#include <string.h>
#include <stdlib.h>
#include <mysql.h>
#include <stdio.h>
#include <json-c/json_object.h>

#include <assert.h>
#include "cc_common_mysql.h"

static int load_algo_callback(void *info_obj, int num, char **row, unsigned long *lengths)
{
    assert(num == 4);

    struct json_object *info_object = (struct json_object *) info_obj;
    struct json_object *val, *array_object = NULL;
    if (!json_object_object_get_ex(info_object,"DPS",&array_object)) {
        array_object = json_object_new_array();
        json_object_object_add(info_object,"DPS",array_object);
    }

    val = json_object_new_object();
    json_object_object_add(val, "id", json_object_new_int(atoi(row[0])));
    json_object_object_add(val, "name", json_object_new_string_len(row[1], lengths[1]));
    json_object_object_add(val, "label",json_object_new_string_len(row[2], lengths[2]));
    json_object_object_add(val, "desc", json_object_new_string_len(row[3], lengths[3]));
    json_object_array_add(array_object, val);

    return 0;
}

int test_query_ex()
{
    char     sql[4096];
    size_t   len;
    FILE    *fp;

    printf("%-20s", "SELECT...");
    struct json_object *jobj = json_object_new_object();
    len = snprintf(sql, sizeof(sql), "SELECT id,name,label,description FROM "
                   "casb_field_tokenization_algo");
    if (ck_mysql_exec_ex(sql, len, load_algo_callback, jobj))
        return 1;
    printf("ok\n");

    if ((fp = fopen("/tmp/result.txt", "w")) != NULL) {
        len = snprintf(sql, sizeof(sql), "%s", json_object_to_json_string_ext(jobj, 0));
        printf("%zu bytes result write to /tmp/result.txt\n", fwrite(sql, 1, len, fp));
        fclose(fp);
    }
    json_object_put(jobj);

    return 0;
}

static int abort_callback(void *value, int num, char **row, unsigned long *lengths)
{
    int x = *(int *)value;
    if ((x % 2))
        return 1;

    return 0;
}

int test_abnormal_query()
{
    char               sql[1024];
    int                i, len;
    MYSQL_RES         *result;

    len = snprintf(sql, sizeof(sql), "SELECT id,name,label,type_id FROM "
                   "");
    for (i=0; i<10; ++i) {
        result = NULL;
        if (ck_mysql_exec(sql, len, (void **)&result) || result == NULL)
            return 1;
        printf("Rows:%lld ", mysql_num_rows(result));
        mysql_free_result(result);
    }
    printf("\n\n");

    for (i=0; i<10; ++i) {
        result = NULL;
        if (i < 5) {
            if (cc_mysql_exec_ex(sql, len, abort_callback, &i))
                return 8;
        } else {
            if (cc_mysql_exec_ex(sql, len, NULL, &i))
                return 8;
        }

        mysql_free_result(result);
    }

    return 0;
}

int test_insert()
{
    int  len;
    char sql[1024];

    printf("%-20s", "INSERT...");
    len = snprintf(sql, sizeof(sql), "INSERT INTO (id,name,type_id) "
                   "VALUES(1000000,'Test Algo', 1000000)");
    if (cc_mysql_exec(sql, len, NULL))
        return 1;
    printf("ok\n");

    return 0;
}

int test_update_delete()
{
    int  len;
    char sql[1024];

    printf("%-20s", "UPDATE...");
    len = snprintf(sql, sizeof(sql), "UPDATE  SET type_id=20000 "
                   "WHERE id=1000000");
    if (cc_mysql_exec(sql, len, NULL))
        return 4;
    printf("ok\n");

    printf("%-20s", "DELETE...");
    len = snprintf(sql, sizeof(sql), "DELETE FROM  WHERE id=1000000");
    if (cc_mysql_exec(sql, len, NULL))
        return 5;
    printf("ok\n");

    return 0;
}

int test_excape_string(const char *fname, const char *path)
{
    size_t len, valsz;
    char sql[1024], *estr;

    printf("\n============ No Escape Case ============\n");
    len = snprintf(sql, sizeof(sql),
                   "INSERT INTO (fname,upload_date,md5,sha1,store_path) "
                   "VALUES('%s', 0,'','','%s');", fname, path);

    printf("orig: %s(%zu)\n", sql, len);

    if (cc_mysql_exec(sql, len, NULL))
        printf("expect error\n");

    printf("\n============ Escape Case ============\n");
    valsz = strlen(fname);
    estr = (char *) calloc(1, 2*valsz + 1);
    len = cc_mysql_escape_string(fname, valsz, estr);
    len = snprintf(sql, sizeof(sql),
                   "INSERT INTO (fname,upload_date,md5,sha1,store_path) "
                   "VALUES('%s', 0,'','','%s');", estr, path);
    printf("escape: %s(%zu)\n", sql, len);
    free(estr);

    if (cc_mysql_exec(sql, len, NULL))
        return 1;

    return 0;
}

int main(int argc, char *argv[])
{
    mysql_connection_t uri;
    uri.host = "127.0.0.1";
    uri.port = 3306;
    uri.username = "root";
    uri.password = "root";
    uri.dbname = "";

    if (ck_mysql_init(&uri))
        return 1;
    ck_mysql_close();
    if (ck_mysql_init(&uri))
        return 1;
    if (ck_mysql_init(&uri))
        return 1;


    const char *fname = "Andrew's file''''name'''";
    const char *fpath = "E:\\file\\pathname/to/`!@#$%^&*()_+";
    assert(test_excape_string(fname, fpath) == 0);

    assert(test_insert() == 0);
    assert(test_query_ex() == 0);
    assert(test_update_delete() == 0);
    assert(test_abnormal_query() == 0);

    cc_mysql_close();
    return 0;
}
