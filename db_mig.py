import json
import sys
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client.dbquiz


def export_db(coll_name, fname=''):
    file_name = 'imported_' + coll_name
    if fname != '':
        file_name = fname

    all = list(db[coll_name].find({}, {'_id': False}))
    with open(file_name, 'w', encoding='utf8') as f:
        for row in all:
            f.write(json.dumps(row) + '\n')


def import_db(coll_name, fname):
    if fname is None or fname == '':
        raise RuntimeError('Provide file name')

    if coll_name is None or coll_name == '':
        raise RuntimeError('Provide collection name')

    with open(fname, 'r', encoding='utf8') as f:
        for line in f.readlines():
            obj = json.loads(line.replace('\n', ''))
            db[coll_name].insert_one(obj)


if __name__ == '__main__':
    oper = sys.argv[1]
    if oper == 'import':
        if len(sys.argv) < 4:
            raise RuntimeError('db_mig.py import collection_name file_name')
        import_db(sys.argv[2], sys.argv[3])
    elif oper == 'export':
        if len(sys.argv) < 3:
            raise RuntimeError('db_mig.py export collection_name file_name(optional)')
        if len(sys.argv) == 3:
            export_db(sys.argv[2])
        else:
            export_db(sys.argv[2], sys.argv[3])
