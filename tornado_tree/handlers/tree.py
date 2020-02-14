from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from tornado.web import RequestHandler, Finish
from tornado_sqlalchemy import SessionMixin, as_future
from tornado_tree.models import TreeNode, TreeNotEmptyError


class TreeHandler(SessionMixin, RequestHandler):
    """
    For testing purposes
    content-type: text/plain
    """

    async def get(self):
        with self.make_session() as session:
            node_count = await as_future(lambda: session.query(TreeNode).count())
            if node_count > 0:
                for node in await as_future(
                        lambda:
                        session.query(TreeNode)
                        .order_by(TreeNode.path)):
                    # Not using a list for response in order to save RAM
                    self.write(node.to_json())

            else: self.write({'error': 'The tree is empty yet'})


class NodeHandler(SessionMixin, RequestHandler):
    """
    For handling requests to the tree structure
    content-type: application/json
    """

    # Exit the current handler, if possible
    # raise HTTPError(...) would break interface consistency
    def exit_on_error(self, error: str):
        self.write({'error': error})
        raise Finish()

    @staticmethod
    async def find_node(session, node_id: int) -> TreeNode:
        return await as_future(
                lambda:
                session.query(TreeNode)
                .filter(TreeNode.id == node_id)
                .one())

    async def get(self, node_id: int):
        with self.make_session() as session:
            try:
                node = await self.__class__.find_node(session, node_id)
                response = node.to_json()

            # Expecting sqlalchemy exceptions to be propagated
            except NoResultFound:
                self.exit_on_error('Node not found')

            # Must not happen (check id_seq consistency)
            except MultipleResultsFound:
                self.exit_on_error('Multiple nodes with the same ID')

        self.write(response)

    async def post(self):
        req_kwargs = {
                'name': self.get_argument('name', strip = False),
                'data': self.get_argument('data', default = '', strip = False),
                'parent': self.get_argument('parent', default = None, strip = False)}

        with self.make_session() as session:
            if req_kwargs['parent'] is not None:
                # Extract parent node ID
                try:
                    parent_id = int(req_kwargs['parent'])

                except ValueError:
                    self.exit_on_error('Invalid parent node ID')

                # Find the parent node, if any
                try:
                    parent_node = await self.__class__.find_node(session, parent_id)

                except:
                    self.exit_on_error('Parent node not found')

            else: parent_node = None

            # Register the new node
            try:
                new_node = TreeNode.from_dict(req_kwargs, parent = parent_node)
                await new_node.register(session)

                response = new_node.to_json()

                session.add(new_node)
                session.commit()

            except TreeNotEmptyError as e:
                self.exit_on_error(str(e))

        self.write(response)

    async def put(self, node_id):
        pass

    async def delete(self, node_id):
        pass


