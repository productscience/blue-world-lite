'''
Edit ``postgresql.conf``

::

    listen_addresses = '*'

Edit ``pg_hba.conf``:

::

    host    all       all   0.0.0.0/0     md5

Restart the server for the changes to `postgres,conf` and `pg_ba.conf`
to be reflected:

::
    sudo service postgresql restart

Set up a user for migrating data out of the previous database:
::

    CREATE USER migrate WITH PASSWORD 'migrate';
    GRANT ALL PRIVILEGES ON DATABASE grocom to migrate;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO migrate;

Make sure we have have defined a port to allow outside access
from the host machine, to the guest VM:

::

    Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
      config.ssh.forward_agent = true

        config.vm.define "main" do |machine|
            machine.vm.box = "trusty64"
                # for postgres access
                machine.vm.network "forwarded_port", guest: 5432, host: 8032

Make sure new port forwarding is active, so we can connect to the guest VM
database:

::
    vagrant reload

'''

from decimal import Decimal
import datetime
import json
import psycopg2
from psycopg2.extras import DictCursor
import pytz


def run(dsn, path, out=print):
    """

    Writes a stream of output to a provided

    dsn: a String that psycopg2 uses to connect to Postgres
    path: a String listing the filename to write to
    out: a Callable used to sending logs to
    """
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor(cursor_factory=DictCursor)

    with open(path, 'wb') as fp:
        fp.write(b'[\n')
        out("Migrating bag type ...")
        migrate_bag_type(cursor, fp, out)
        out("\ndone.")
        out("Migrating collection points ...")
        migrate_collection_points(cursor, fp, out)
        out("\ndone.")
        fp.write(
            json.dumps(
                {
                    "model": "sites.site",
                    "pk": 1,
                    "fields": {
                        "domain": 'localhost',
                        "name": 'BlueWorld',
                    }
                },
                indent=4,
            ).encode('utf8')
        )
        fp.write(b',\n')
        fp.write(
            json.dumps(
                {
                    "model": "join.customertag",
                    "pk": 1,
                    "fields": {
                        "tag": "Starter"
                    }
                },
                indent=4,
            ).encode('utf8')
        )
        fp.write(b'\n')
        fp.write(b']')


def migrate_collection_points(cursor, fp, out):
    cursor.execute('''
        select
            id
          , name
          , "where"
          , latitude
          , longitude
          , available
          , display_order
        from joinforms_pickuppoint
        where group_id=1
    ''')
    for i, row in enumerate(cursor.fetchall()):
        out('.', end='')
        fp.write(
            json.dumps(
                {
                    "model": "join.collectionpoint",
                    "pk": row['id'],
                    "fields": {
                        "name": row['name'].strip(),
                        "location": row['where'],
                        "latitude": row['latitude'],
                        "longitude": row['longitude'],
                        "active": row['available'],
                        "display_order": row['display_order'],
                    }
                },
                indent=4,
            ).encode('utf8')
        )
        fp.write(b',\n')


def migrate_bag_type(cursor, fp, out):
    cursor.execute('''
        select
            id
          , name
          , active
          , "order"
          , price
        from joinforms_bagtype
        where group_id=1
    ''')
    for i, row in enumerate(cursor.fetchall()):
        out('.', end='')
        fp.write(
            json.dumps(
                {
                    "model": "join.bagtype",
                    "pk": row['id'],
                    "fields": {
                        "name": row['name'].strip(),
                        "active": row['active'],
                        "display_order": row['order'],
                    }
                },
                indent=4,
            ).encode('utf8')
        )
        fp.write(b',\n')
        fp.write(
            json.dumps(
                {
                    "model": "join.bagtypecostchange",
                    "pk": i,
                    "fields": {
                        "bag_type_id": row['id'],
                        "changed": datetime.datetime.now(tz=pytz.UTC).isoformat(),
                        "weekly_cost": str(Decimal(row['price'])/Decimal(4.0)),
                    }
                },
                indent=4,
            ).encode('utf8')
        )
        fp.write(b',\n')


if __name__ == '__main__':
    run('dbname=grocom user=migrate password=migrate port=8032 host=localhost', 'initial.json', print)
