from packages.core.db import ConnectionsDB
from packages.core.utils.config import Config

class AnicamModel():
    """docstring for CtrlMod1"""

    def __init__(self):
        self.name_connection = 'threepersonteam'
        self.id = None

    async def get_id(self):
        if not self.id:
            query = "SELECT id FROM shipping_shipperinternational WHERE nickname='anicam'"
            shipper = await(await ConnectionsDB().get_connection(self.name_connection)).select(query)
            self.id = shipper[0]['id']
        return self.id

    async def select_products(self, zip_code='04530', country='mx'):
        await self.get_id()
        query = f"""SELECT package_id
            FROM shipping_shippinginternational
            WHERE
                shipper_id={self.id} AND
                zipcode="{zip_code}" AND
                country="{country}"
        """
        products_with_price_draw = await(await ConnectionsDB().get_connection(self.name_connection)).select(query)
        products_with_price = ', '.join([str(i['package_id']) for i in products_with_price_draw])
        """
        Los if son para los productos que no tienen un tamaño por defecto.
        El condicional de category_name. Es temporal. Mientras se termina de sincronizar los productos de buzzcaloMx
        """
        query = """
            SELECT
                id,
                IF(length, length, 10) AS length,
                IF(height, height, 10) AS height,
                IF(width, width, 10) AS width,
                IF(weight, weight, 1.5) AS weight,
                cost_price
            FROM
                store_product
            WHERE
                cost_price > 0  AND
                ship_price >= 0 AND
                category_name IS NOT NULL
            """
        if products_with_price:
            query += f'AND id NOT IN ({products_with_price})'
        query += " LIMIT 200;"
        return await(await ConnectionsDB().get_connection(self.name_connection)).select(query)

    async def insert_shippings(self, ships:list):
        await self.get_id()
        if ships:
            for ship in ships:
                ship['country']='mx'
                ship['zipcode']='04530'
                ship['shipper_id']=self.id
            return await (
                await ConnectionsDB().get_connection(self.name_connection)
            ).insert(ships, 'shipping_shippinginternational', ['id'])