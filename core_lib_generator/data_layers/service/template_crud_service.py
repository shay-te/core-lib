from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib_generator.data_layers.data_access.template_crud_data_access import TemplateCRUDDataAccess


class TemplateCrudService(Service):

    def __init__(self, template_da: TemplateCRUDDataAccess):
        self._template_da = template_da

    @ResultToDict()
    def get(self, id: int):
        return self._template_da.get(id)

    def update(self, id: int, data: dict):
        self._template_da.update(id, data)

    @ResultToDict()
    def create(self, data: dict):
        return self._template_da.create(data)

    def delete(self, id: int):
        self._template_da.delete(id)
