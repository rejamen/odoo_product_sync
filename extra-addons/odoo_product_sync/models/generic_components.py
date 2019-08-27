# -*- coding: utf-8 -*-

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import IDMissingInBackend


class GenericAdapter(AbstractComponent):
    """Generic interface to speak with the backend.

    It translate the basic orders (search, read, write) to the
    protocolsused by the backend.

    Adapter in this connector should _inherit it.
    """
    _name = 'generic.adapter'
    _inherit = ['base.backend.adapter']
    _usage = 'backend.adapter'

    _external_model = None

    def search(self, filters=None):
        """Search records according to some criterias.

        Return a list of IDs.
        """
        return self._call('%s.search' % self._external_model,
                          [filters] if filters else [{}])

    def read(self, id, attributes=None):
        """Return the information of a record."""
        arguments = [int(id)]
        if attributes:
            arguments.append(attributes)
        return self._call('%s.info' % self._external_model, arguments)

    def search_read(self, filters=None):
        """Search records according to some criterias and
        return their information."""
        return self._call('%s.list' % self._external_model, [filters])

    def create(self, data):
        """Create a record on the external system."""
        return self._call('%s.create' % self._external_model, [data])

    def write(self, id, data):
        """Update records in the external system."""
        return self.write('%s.write' % self._external_model, [int(id), data])

    def delete(self, id):
        """Delete a record on external system."""
        return self.unlink('%s.unlink' % self._external_model, [int(id)])


class GenericImportMapper(AbstractComponent):
    """Abstract Component for Import Mappers.

    Custom Import Mappers shoud _inherit it.
    """
    _name = 'generic.import.mapper'
    _inherit = ['base.import.mapper']
    _usage = 'import.mapper'


class GenericImporter(AbstractComponent):
    """Generic Importer for external service.

    Custom Importers should _inherit it.
    """
    _name = 'generic.importer'
    _inherit = 'base.importer'
    _usage = 'record.importer'

    def __init__(self, work_context):
        super(GenericImporter, self).__init__(work_context)
        self.external_id = None
        self.external_record = None

    def _get_external_data(self):
        """Return the raw external data for self.eternal_id."""
        return self.backend_adapter.read(self.external_id)

    def _before_import(self):
        """Hook called before the import."""

    def _map_data(self):
        """Return an instance of MapRecord."""
        return self.mapper.map_record(self.external_record)

    def _validate_data(self, data):
        """Check if values to import are correct."""
        return

    def _get_binding(self):
        return self.binder.to_internal(self.external_id)

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _create(self, data):
        """Create the Odoo record."""
        self._validate_data(data)
        model = self.model.with_context(connector_no_export=True)
        binding = model.create(data)
        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """Update an Odoo record."""
        self._validate_data(data)
        binding.with_context(connector_no_export=True).write(data)
        return

    def _after_import(self, binding):
        """Called at the end of import."""
        return

    def run(self, external_id, force=False):
        """Run the synchronization."""
        self.external_id = external_id
        try:
            self.external_record = self._get_external_data()
        except IDMissingInBackend:
            return ('Record does not longer exists in external source.')

        binding = self._get_binding()
        map_record = self._map_data()

        if binding:
            record = self._update_data(map_record)
            self._update(binding, record)
        else:
            record = self._create_data(map_record)
            binding = self._create(record)

        self.binder.bin(self.external_id, binding)
        self._after_import(binding)
