
from persistence.databases import DocumentNotFound


class SeqNumGenerator:
    """
    Database SeqNumGenerator é responsável por persistir números sequenciais
    em um DBManager.

    db_manager:
        Instância do DBManager para persistir registros de número sequencial
    """

    def __init__(self, db_manager, seqnum_label):
        self.db_manager = db_manager
        self.seqnum_label = seqnum_label

    def new(self):
        record = self.get()
        record['SEQ'] += 1
        self._update(record)
        return record['SEQ']

    def get(self):
        """
        Obtém o registro de um número sequencial.
        No caso de o registro não existir, cria o registro.

        Retorno:
        registro de um número sequencial registrado na base de dados
        """
        try:
            record = self._read()
        except DocumentNotFound:
            self._create({'SEQ': 0})
            record = self._read()
        return record

    def _read(self):
        """
        Obtém registro de um número sequencial por seu ID na base de dados.

        Retorno:
        registro de um número sequencial registrado na base de dados

        Erro:
        DocumentNotFound: registro não encontrado na base de dados.
        """
        return self.db_manager.read(self.seqnum_label)

    def _create(self, record):
        """
        Persiste registro de um número sequencial.

        Params:
        record: registro de número sequencial
        """
        self.db_manager.create(self.seqnum_label, record)

    def _update(self, record):
        """
        Atualiza o registro de um número sequencial.

        Params:
        record: registro de número sequencial a ser atualizado

        Erro:
        DocumentNotFound: registro não encontrado na base de dados.
        """
        self.db_manager.update(self.seqnum_label, record)
