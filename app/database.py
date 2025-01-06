from mysql.connector import pooling

class Database:
    _connection_pool = None

    @staticmethod
    def initialize_connection_pool(config):
        """
        Inicializa el pool de conexiones con los parámetros proporcionados.
        """
        Database._connection_pool = pooling.MySQLConnectionPool(
            pool_name="flask_pool",
            pool_size=5,  # Número de conexiones en el pool
            **config
        )

    @staticmethod
    def get_connection():
        """
        Obtiene una conexión del pool.
        """
        if Database._connection_pool is None:
            raise Exception("Connection pool is not initialized. Call initialize_connection_pool() first.")
        return Database._connection_pool.get_connection()
