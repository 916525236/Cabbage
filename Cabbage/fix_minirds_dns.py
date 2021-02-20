#!/usr/bin/python

import MySQLdb
import MySQLdb.cursors
import commands

def do_select_fetchall(sqlstr, args=None, as_dict=True):
    """
    Remarks:
        Do a query and return a recordset.
        share_conn_thread describe whether the connection object is from PooledDB or PersistentDB
    """
    hostip, user, passwd, port, dbname = '127.0.0.1', 'aurora', 'aurora@test', 3306, 'dbaas'
    result = []
    conn = MySQLdb.connect(
        host=str(hostip),
        user=str(user),
        passwd=str(passwd),
        db=str(dbname),
        port=port,
        charset="utf8",
        connect_timeout=5)
    try:
        if as_dict:
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        else:
            cursor = conn.cursor()
        cursor.execute(sqlstr, args)
        rows = cursor.fetchall()
        for row in rows:
            result.append(row)
        cursor.close()
    finally:
        if conn:
            conn.close()
    return result


def get_conn_addr():
    sql = 'select * from custins_conn_addr'
    custlist = do_select_fetchall(sql)
    upsqllist = {}
    for cust in custlist:
        conn = cust['conn_addr_cust']
        id = cust['custins_id']
        status, output = commands.getstatusoutput("nslookup %s |grep Address|grep -v '#'| awk -F ':' '{print $2}'"% conn)
        masterip = output.split('\n')[0].replace(' ', '')
        if not masterip:
            print 'nslookup %s failed' % conn
            continue
        inslist =  do_select_fetchall('select  i.custins_id, i.id, hi.ip, ias.role from instance i, hostinfo hi, instance_stat ias where i.id=ias.ins_id and i.host_id=hi.id and i.custins_id=%s' % id)
        insdict = {ins['ip']: ins for ins in inslist}
        updict = {}
        masterins = insdict.pop(masterip)
        if masterins['role'] != 0:
            updict[masterins['id']] = 0
            updict[insdict[insdict.keys()[0]]['id']] = 1
        if updict:
            print conn, 'master ip', masterip, 'dbaas db master ip', [ins['ip'] for ins in inslist if ins['role']==0][0]
        for up in updict:
            upsqllist.setdefault(conn, []).append('update instance_stat set role=%s where ins_id=%s;' % (updict[up], up))
    
    for conn in upsqllist:
        print ' '
        print 'need up %s' % conn
        for sql in upsqllist[conn]:
            print sql

get_conn_addr()