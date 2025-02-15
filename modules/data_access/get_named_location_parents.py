#!/usr/bin/env python3
from typing import Dict, List, Optional
from contextlib import closing

from psycopg2 import extensions


def get_named_location_parents(connection: extensions.connection, named_location_id: int) -> Optional[Dict[str,str]]:
    """
    Get the site of a named location.

    :param connection: A database connection.
    :param named_location_id: A named location ID.
    :return: The site.
    """
    parents: Dict[str,str] = {}
    with closing(connection.cursor()) as cursor:
        find_parent(cursor, named_location_id, parents)
    if not parents:
        return None
    else:
        return parents


def find_parent(cursor: extensions.cursor, named_location_id: int, parents: Dict[str,str]):
    """
    Recursively search for the site.

    :param cursor: A database cursor object.
    :param named_location_id: The named location ID.
    :param parents: Collection to append to.
    """
    sql = '''
        select
            prnt_nam_locn_id, nam_locn.nam_locn_name, type.type_name
        from
            nam_locn_tree
        join
            nam_locn on nam_locn.nam_locn_id = nam_locn_tree.prnt_nam_locn_id
        join
            type on type.type_id = nam_locn.type_id
        where
            chld_nam_locn_id = %s
    '''
    cursor.execute(sql, [named_location_id])
    row = cursor.fetchone()
    if row is not None:
        parent_id = row[0]
        name = row[1]
        type_name = row[2]
        if type_name.lower() == 'site':
            parents['site'] = name
        if type_name.lower() == 'domain':
            parents['domain'] = name        
        find_parent(cursor, parent_id, parents)
