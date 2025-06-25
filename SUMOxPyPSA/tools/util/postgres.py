from .which import which
try:
    import psycopg2
    import psycopg2.extensions
except ImportError:
    psycopg2 = False

PSQL       = which('psql')

class QueryError(Exception):
    def __init__(self, error, query):
        super(QueryError, self).__init__(error)
        self.query = query

def make_copy_query(subquery_or_table):
    if subquery_or_table.lower().startswith('select'):
        query = 'COPY ({0}) TO STDOUT WITH CSV HEADER'
    else:
        query = 'COPY {0} TO STDOUT WITH CSV HEADER'
    return query.format(subquery_or_table)


class PsqlWrapper(object):
    "Wrap psql client executable under subprocess"
    def check_connection(self):
        try:
            self.do_query('SELECT 1')
        except QueryError as e:
            return False
        else:
            return True

    def update_params(self, params):
        for n,v in params.items():
            k = 'PG' + n.upper()
            os.environ[k] = str(v)

    def do_createdb(self, database_name):
        self.do_query('CREATE DATABASE {0}'.format(database_name))

    def do_query(self, query):
        try:
            subprocess.check_call([PSQL, '-v', 'ON_ERROR_STOP=1', '-c', query])
        except subprocess.CalledProcessError as e:
            raise QueryError(e, query)
        except OSError as e:
            raise Exception(e)

    def do_queryfile(self, queryfile):
        try:
            subprocess.check_call([PSQL, '-v', 'ON_ERROR_STOP=1', '-f', queryfile])
        except subprocess.CalledProcessError as e:
            raise QueryError(e, queryfile)
        except OSError as e:
            raise Exception(e)

    def do_getcsv(self, subquery_or_table, io_handle):
        query = make_copy_query(subquery_or_table)
        try:
            command = [PSQL, '-v', 'ON_ERROR_STOP=1', '-c', query]
            try:
                subprocess.check_call(command, stdout=io_handle)
            except io.UnsupportedOperation as e:
                io_handle.write(subprocess.check_output(command).decode('utf-8'))
        except subprocess.CalledProcessError as e:
            raise QueryError(e, subquery_or_table)
        except OSError as e:
            raise Exception(e)


class Psycopg2Wrapper(object):
    "Wrap psycopg2 for consistency with psql-wrapper"
    def __init__(self):
        self._connection = None
        self._params     = dict()

    def update_params(self, params):
        if self._connection is not None:
            # close existing connection
            if not self._connection.closed:
                self._connection.close()
            self._connection = None
        self._params.update(**params)

    def check_connection(self):
        try:
            if self._connection is None:
                self._connection = psycopg2.connect(**self._params)
        except (TypeError, psycopg2.Error) as e:
            return False
        else:
            return True

    def do_createdb(self, database_name):
        self._connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.do_query('CREATE DATABASE {0};'.format(database_name))

    def do_query(self, query):
        try:
            with self._connection as con:
                with con.cursor() as cursor:
                    cursor.execute(query)
        except psycopg2.Error as e:
            raise QueryError(e, query)

    def do_queryfile(self, queryfile):
        with io.open(queryfile, 'r', encoding='utf-8') as handle:
            query = handle.read()
        self.do_query(query)

    def do_getcsv(self, subquery_or_table, io_handle):
        query  = make_copy_query(subquery_or_table)
        try:
            with self._connection.cursor() as cursor:
                cursor.copy_expert(query, io_handle)
        except psycopg2.Error as e:
            raise QueryError(e, query)



class PgWrapper(Psycopg2Wrapper if psycopg2 else PsqlWrapper):
    '''
Wrap interfaces of either psycopg2 or psql-under-subprocess
Which of these is actually implemented depends on the runtime
environment; psycopg2 is given preference, but psql is a fallback.
'''
    pass
