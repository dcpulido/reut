import json
import logging
import unittest
import mysql.connector
from mysql.connector import errorcode


class MysqlDAO:

    def __init__(self,
                 conf):
        self.conf = conf
        self._spec = {}
        self.connect_to_database()
        self.get_schema()

    def connect_to_database(self):
        try:
            self.cnx = mysql.connector.connect(user=self.conf["user"],
                                               password=self.conf["password"],
                                               host=self.conf["host"],
                                               database=self.conf["database"],
                                               port=3306)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.info(
                    "Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.info("Database does not exist")
            else:
                logging.info(err)

    def insert(self,
               ob):
        keys = ""
        values = "VALUES ("
        for k in ob.to_dict().keys():
            if k != "idUser":
                def ret(x): return '%(' + k + ')s, ' \
                    if type(x).__name__ == "str" \
                    or type(x).__name__ == "unicode" \
                    else '%('+str(x)+')s, '
                values += ret(k)
                keys += k + \
                    ", "
        values = values[:len(values)-2] + ")"
        keys = keys[:len(keys)-2] + ") "
        query = "INSERT INTO " + \
            ob.__class__.__name__ + \
            " (" + \
            keys + \
            values
        return self.execute_query(query,
                                  module_name,
                                  ob=ob)

    def get_by_id(self,
                  id,
                  module_name):
        instance = Instance()
        instance.__class__.__name__ = module_name

        def ret(x): return '"'+x+'"' \
            if type(x).__name__ == "str" \
            or type(x).__name__ == "unicode" \
            else str(x)
        ids = ""
        for kk in self._spec[module_name]:
            if kk in id.keys():
                ids += kk + \
                    "=" +\
                    ret(id[kk]) + \
                    " AND "
        ids = ids[:len(ids)-5]
        query = "SELECT * " + \
            ", ".join(instance.to_dict().keys()) + \
            " FROM " + \
            module_name + \
            " WHERE " + \
            ids
        return self.execute_query(query,
                                  module_name,
                                  one_result=True)

    def get_by_arg(self,
                   arg,
                   module_name,
                   dictionary=False):
        instance = Instance()
        instance.__class__.__name__ = module_name

        def ret(x): return '"'+x+'"' \
            if type(x).__name__ == "str" \
            or type(x).__name__ == "unicode" \
            else str(x)
        ids = ""
        for kk in arg.keys():
            ids += kk + \
                "=" +\
                ret(arg[kk]) + \
                " AND "
        ids = ids[:len(ids)-5]
        query = "SELECT * " + \
            ", ".join(instance.to_dict().keys()) + \
            " FROM " + \
            module_name + \
            " WHERE " + \
            ids
        return self.execute_query(query,
                                  module_name,
                                  one_result=True,
                                  dictionary=dictionary)

    def get_all(self,
                module_name):
        query = "SELECT  * FROM " + \
                module_name
        return self.execute_query(query,
                                  module_name)

    def delete(self,
               id,
               module_name):
        def ret(x): return '"'+x+'"' \
            if type(x).__name__ == "str" \
            or type(x).__name__ == "unicode" \
            else str(x)
        ids = ""
        for kk in id.keys():
            ids += kk + \
                "=" +\
                ret(id[kk]) + \
                " AND "
        ids = ids[:len(ids)-5]

        query = "DELETE FROM " + \
                module_name + \
                " WHERE " + \
                ids
        return self.execute_query(query,
                                  module_name)

    def update(self,
               ob):
        def ret(x): return '"'+x+'"' \
            if type(x).__name__ == "str" \
            or type(x).__name__ == "unicode" \
            else str(x)
        ww = " WHERE "
        for k in self._spec[ob.__class__.__name__]:
            ww += k + \
                "=" + \
                ret(ob.to_dict()[k]) + \
                " AND "
        ww = ww[:len(ww)-5]
        sets = " SET "
        for k in ob.to_dict().keys():
            sets += k +\
                "=%s, "
        sets = sets[:len(sets)-2]
        query = "UPDATE " + \
                ob.__class__.__name__ + \
                sets + \
                ww
        return self.execute_query(query,
                                  module_name,
                                  ob=ob)

    def execute_query(self,
                      query,
                      module_name,
                      ob=None,
                      one_result=False,
                      dictionary=False):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            if query[:6] == "SELECT":
                cursor.execute(query)
                toret = []
                for c in cursor:
                    if not dictionary:
                        instance = None
                        if c is not None:
                            instance = Instance()
                            instance.__class__.__name__ = module_name
                            instance.set_by_dic(c)
                            toret.append(instance)
                    else:
                        toret.append(c)
                cursor.close()
                if one_result:
                    return toret[0]
                else:
                    return toret
            if query[:6] == "INSERT":
                cursor.execute(query, ob.to_dict())
                lsid = cursor.lastrowid
                self.cnx.commit()
                cursor.close()
                return lsid
            if query[:6] == "DELETE":
                cursor.execute(query)
                self.cnx.commit()
            if query[:6] == "UPDATE":
                cursor.execute(query,
                               ob.to_dict().values())
                self.cnx.commit()

            cursor.close()
            return "ok"

        except Exception, e:
            logging.info(e)
            return None
        except Exception, e:
            logging.info(e)
            logging.info("error in get all returning []")
            return None

    def get_schema(self):
        try:
            cursor = self.cnx.cursor(dictionary=True)
            query = 'select * ' + \
                'from INFORMATION_SCHEMA.COLUMNS ' + \
                ' where table_schema="' + \
                self.conf["database"] + \
                '";'
            cursor.execute(query)
            tt = {}
            for att in cursor:
                if att["COLUMN_KEY"] == "PRI":
                    if att["TABLE_NAME"] in self._spec:
                        self._spec[att["TABLE_NAME"]].append(
                            att["COLUMN_NAME"])
                    else:
                        self._spec[att["TABLE_NAME"]] = [att["COLUMN_NAME"]]
            cursor.close()
        except Exception, e:
            logging.info(e)

    def disconnect(self):
        self.cnx.close()


class Instance:

    def __init__(self,
                 dic={}):
        if dic != {}:
            self.set_by_dic(dic)

    def to_dict(self):
        toret = {}
        for k in self.__dict__.keys():
            if k != "__name__":
                toret[k] = self.__dict__[k]
        return toret

    def get_id(self):
        tt = {}
        for att in self._spec[self.__class__.__name__]:
            try:
                tt[att.keys()[0]] = self.to_dict[att]
            except:
                tt[att.keys()[0]] = ""
        return tt

    def set_by_dic(self,
                   arr):
        if len(self.to_dict().keys()) == 0:
            for k in arr.keys():
                aux = ""
                if type(arr[k]).__name__ == "datetime":
                    aux = str(arr[k])
                    setattr(self, k, aux)
                else:
                    setattr(self, k, arr[k])
        for k in self.to_dict().keys():
            if k in arr.keys():
                if type(arr[k]).__name__ == "datetime":
                    aux = str(arr[k])
                    setattr(self, k, aux)
                else:
                    setattr(self, k, arr[k])


class TestMysqlDAO(unittest.TestCase):
    def test_instance_to_dict(self):
        ini = dict(name="name",
                   tlf=88)
        ins = Instance(ini)
        self.assertEqual(ins.to_dict(), ini)

    def test_instance_constructor(self):
        ini = dict(name="name",
                   tlf=88)
        ins = Instance(ini)
        self.assertEqual(ins.name, "name")

    def test_instance_set_by_dict(self):
        ini = dict(name="name",
                   tlf=88)
        ins = Instance()
        ins.set_by_dic(ini)
        self.assertEqual(ins.to_dict(), ini)


if __name__ == '__main__':
    unittest.main()
