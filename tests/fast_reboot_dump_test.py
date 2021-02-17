import json
import os
from utilities_common.db import Db
import importlib
fast_reboot_dump = importlib.import_module("scripts.fast-reboot-dump")

class TestFastRebootDump(object):

    @classmethod
    def setup_class(cls):
        print("SETUP")

        target = os.getcwd() + '/fast_reboot_dump_dbs'
        asic_db_object = Db()
        app_db_object = Db()
        asic_db = asic_db_object.db
        app_db = app_db_object.db
        populate_db(asic_db, target, 'ASIC_DB.json')
        populate_db(app_db, target, 'APP_DB.json')

        cls.asic_db = asic_db
        cls.app_db = app_db

    def test_generate_fdb_entries_vlan_portcahnnel_member(self):
        vlan_ifaces = ['Vlan2']

        fdb_entries, all_available_macs, map_mac_ip_per_vlan = fast_reboot_dump.generate_fdb_entries_logic(self.asic_db, self.app_db, vlan_ifaces)
        expectd_fdb_entries = """\
[{'FDB_TABLE:Vlan2:52-54-00-5D-FC-B7': {'type': 'dynamic', 'port': 'PortChannel0001'}, 'OP': 'SET'}]\
"""
        assert str(fdb_entries) == expectd_fdb_entries

        expectd_all_available_macs = """\
{('Vlan2', '52:54:00:5d:fc:b7')}\
"""
        assert str(all_available_macs) == expectd_all_available_macs

        expectd_map_mac_ip_per_vlan = """\
{'Vlan2': {'52:54:00:5d:fc:b7': 'PortChannel0001'}}\
"""
        assert str(map_mac_ip_per_vlan) == expectd_map_mac_ip_per_vlan
    
    @classmethod
    def teardown_class(cls):
        print("TEARDOWN")

def populate_db(dbconn, target, db_name):
    if (db_name == 'ASIC_DB.json'):
        db = dbconn.ASIC_DB
    elif (db_name == 'APP_DB.json'):
        db = dbconn.APPL_DB
    with open(target + '/' + db_name) as DB:
        db_dump = json.load(DB)
        DB.close()
        for (table, fields) in db_dump.items():
            for (key, value) in fields['value'].items():
                dbconn.set(db, table, key, value)
