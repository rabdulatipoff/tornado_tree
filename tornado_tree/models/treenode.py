from __future__ import annotations
from typing import Optional
import json

from sqlalchemy import Index, Column, Integer, String, Sequence
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, foreign, remote
from sqlalchemy_utils import LtreeType, Ltree
from tornado.options import options
from tornado_sqlalchemy import SQLAlchemy, as_future
from tornado_tree.dbconn import db_object, make_url


db = db_object(make_url(options))


# subpath(ltree, int offset, int len)
# Leaving the child out of the parent chain (len = -1)
def get_rootpath(path):
    return func.subpath(path, 0, -1)


class TreeNode(db.Model):

    __tablename__ = 'nodelist'

    id = Column(
            Integer,
            primary_key = True,
            autoincrement = True)
    name = Column(String, nullable = False)
    data = Column(String, nullable = True)
    path = Column(LtreeType, nullable = False)

    __table_args__ = (
            # GiST proved to consume too much RAM without much functional benefit 
            #Index('ix_nodepath', path, postgresql_using = 'gist'),
            Index('ix_nodepath', func.md5(func.ltree2text(path)), postgresql_using = 'btree'),)

    parent = relationship(
            'TreeNode',
            primaryjoin = remote(path) == foreign(get_rootpath(path)),
            backref = 'children',
            # TODO: Enable nodes to switch parents (regen. indices)
            viewonly = True)

    def __init__(self,
            name: str = '',
            data: Optional[str] = '',
            parent: Optional[TreeNode] = None):
        self.name = name
        self.data = data
        self.parent = parent

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'TreeNode(\'{ self.name }\', \'{ self.data }\')'

    async def register(self, session) -> str:
        """
        Obtain and manually set object's id and ltree path
        session must be provided py tornado_sqlalchemy's ThreadPoolExecutor instance
        """
        # Prevent INSERT before instance registration
        with session.no_autoflush:
            # Expected to be zero if the tree is empty
            node_count = await as_future(
                    lambda:
                    session.query(self.__class__)
                    .count())
            # Obtain the next index from the sequence
            id = await as_future(
                    lambda:
                    session.execute(Sequence('nodelist_id_seq')))

        ltree_id = Ltree(str(id))

        # TODO: validate parent's path
        if type(self.parent) is not self.__class__:
            if node_count > 0:
                raise TreeNotEmptyError('Parentless node in non-empty tree')
            else: self.path = ltree_id
        else: self.path = self.parent.path + ltree_id
        self.id = id

        return self.path

    def parent_count(self) -> int:
        """
        Return number of ancestors, excluding self
        """
        return len(self.path) - 1

    def parent_ids(self) -> list:
        """
        Return list of ancestor IDs except the last one (self)
        """

        # FIXME: split( could be slow on a long path; replace with a generator 
        rootpath = self.path.path
        return rootpath.split('.')[:-1]

    def to_json(self, indent: Optional[int] = 0) -> str:
        """
        Serialize node to JSON format
        """

        return json.dumps({
            'id': self.id,
            'name': self.name,
            'data': self.data,
            'parent_count': self.parent_count(),
            'parent_ids': self.parent_ids()
            }, indent = indent)

    @classmethod
    def from_dict(cls, args_dict: dict, parent: Optional[TreeNode] = None):
        """
        Create and initialize a node from a dictionary
        """

        __args__ = 'name', 'data'

        node = cls()
        for key in __args__:
            setattr(node, key, args_dict[key])

        # parent should be an instance
        # TODO: retrieve parent by id here instead of passing a kwarg
        node.parent = parent
        return node


# Handle trying to add multiple root nodes
class TreeNotEmptyError(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


if __name__ == '__main__':
    options.parse_command_line()
    db = db_object(make_url(options))
    db.metadata.create_all(db.engine)
