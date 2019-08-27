# -*- coding: utf-8 -*-

import psycopg2
from contextlib import contextmanager
from datetime import datetime

from odoo import api, fields, models
from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.connector.exception import RetryableJobError
from odoo.addons.queue_job.job import job


class ConnectorBinding(models.AbstractModel):
    """Abstract Model for Bindings in the connector.

    All models used as binding between odoo and external source
    should _inherit it.
    """
    _name = 'connector.binding'
    _description = 'Connector Binding (Abstract)'
    _inherit = 'external.binding'

    # odoo_id field will be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='external.backend',
        string='External Backend',
        required=True,
        ondelete='cascade')
    external_id = fields.Char('ID in external source')

    @job
    @api.model
    def import_batch(self, backend, filters=None):
        """Prepare the import of records modified on external source."""
        if filters is None:
            filters = {}
        with backend.work_on(self._name) as work:
            importer = work.component(usage='batch.importer')
            return importer.run(filters=filters)

    @job
    @api.model
    def import_record(self, backend, external_id, force=False):
        """Import an external record."""
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(external_id, force=force)

    @job
    @api.model
    def export_record(self, fields=None):
        """Export record to external source."""
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage='record.exporter')
            return exporter.run(self, fields)

    @job
    def export_delete_record(self, backend, external_id):
        """Delete record on the external source."""
        with backend.work_on(self._name) as work:
            deleter = work.component(usage='record.exporter.deleter')
            return deleter.run(external_id)


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
        return self._call('%s.update' % self._external_model, [int(id), data])

    def delete(self, id):
        """Delete a record on external system."""
        return self._call('%s.delete' % self._external_model, [int(id)])


class GenericImportMapper(AbstractComponent):
    """Abstract Component for Import Mappers.

    Custom Import Mappers shoud _inherit it.
    """
    _name = 'generic.import.mapper'
    _inherit = ['base.import.mapper']
    _usage = 'import.mapper'


class GenericImporter(AbstractComponent):
    """Generic Importer from external service.

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

    def _is_uptodate(self, binding):
        """Return True if the import should be skipped.

        This could happens because record it is already uo-to-date in
        Odoo.
        """
        assert self.external_record
        if not self.external_record.get('updated_at'):
            return  # no update on external, always import
        if not binding:
            return  # it does not exist so it should not be skipped
        sync = binding.sync_date
        if not sync:
            return
        from_string = fields.Datetime.from_string
        sync_date = from_string(sync)
        external_date = from_string(self.external_record['updated_at'])
        # skip the import if the last sync date is greater than
        # the last update in  external source.
        return external_date < sync_date

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

    def _import_record(self, external_id):
        """Import the record directly."""
        self.model.import_record(self.backend_record, external_id)

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


class GenericExportMapper(AbstractComponent):
    """Base Export Mapper.

    Custom export mappers should _inherit it.
    """
    _name = 'generic.export.mapper'
    _inherit = 'base.export.mapper'
    _usage = 'export.mapper'


class GenericExporter(AbstractComponent):
    """ Base exporter for external source. """
    _name = 'generic.exporter'
    _inherit = 'base.exporter'
    _usage = 'record.exporter'

    def __init__(self, working_context):
        super(GenericExporter, self).__init__(working_context)
        self.binding = None
        self.external_id = None

    def _delay_import(self):
        """ Schedule an import of the record.

        Adapt in the sub-classes when the model is not imported
        using ``import_record``.
        """
        # force is True because the sync_date will be more recent
        # so the import would be skipped
        assert self.external_id
        self.binding.with_delay().import_record(self.backend_record,
                                                self.external_id,
                                                force=True)

    def _should_import(self):
        """ Before the export, compare the update date
        in external source and the last sync date in Odoo,
        if the former is more recent, schedule an import
        to not miss changes done in external source.
        """
        assert self.binding
        if not self.external_id:
            return False
        sync = self.binding.sync_date
        if not sync:
            return True
        record = self.backend_adapter.read(self.external_id,
                                           attributes=['updated_at'])
        if not record['updated_at']:
            # in rare case it can be empty, in doubt, import it
            return True
        sync_date = fields.Datetime.from_string(sync)
        dt_fm = '%Y-%m-%d %H:%M%S'
        external_date = datetime.strptime(record['updated_at'], dt_fm)
        return sync_date < external_date

    def run(self, binding, *args, **kwargs):
        """ Run the synchronization

        :param binding: binding record to export
        """
        self.binding = binding

        self.external_id = self.binder.to_external(self.binding)
        try:
            should_import = self._should_import()
        except IDMissingInBackend:
            self.external_id = None
            should_import = False
        if should_import:
            self._delay_import()

        result = self._run(*args, **kwargs)

        self.binder.bind(self.external_id, self.binding)
        self._after_export()
        return result

    def _run(self):
        """Flow of the synchronization, implemented in inherited classes"""
        raise NotImplementedError

    def _after_export(self):
        """Can do several actions after exporting a record on external."""
        pass

    def _has_to_skip(self):
        """ Return True if the export can be skipped """
        return False

    @contextmanager
    def _retry_unique_violation(self):
        """ Context manager: catch Unique constraint error and retry the
        job later.

        When we execute several jobs workers concurrently, it happens
        that 2 jobs are creating the same record at the same time,
        resulting in:

            IntegrityError: duplicate key value violates unique
            constraint "external_product_product_odoo_uniq"
            DETAIL:  Key (backend_id, odoo_id)=(1, 4851) already exists.

        In that case, we'll retry the import just later.

        .. warning:: The unique constraint must be created on the
                     binding record to prevent 2 bindings to be created
                     for the same external record.
        """
        try:
            yield
        except psycopg2.IntegrityError as err:
            if err.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                raise RetryableJobError(
                    'A database error caused the failure of the job:\n'
                    '%s\n\n'
                    'Likely due to 2 concurrent jobs wanting to create '
                    'the same record. The job will be retried later.' % err)
            else:
                raise

    def _map_data(self):
        """ Returns an instance of
        :py:class:`~odoo.addons.connector.components.mapper.MapRecord`

        """
        return self.mapper.map_record(self.binding)

    def _validate_create_data(self, data):
        """ Check if the values to import are correct

        Pro-actively check before the ``Model.create`` if some fields
        are missing or invalid

        Raise `InvalidDataError`
        """
        return

    def _validate_update_data(self, data):
        """ Check if the values to import are correct

        Pro-actively check before the ``Model.update`` if some fields
        are missing or invalid

        Raise `InvalidDataError`
        """
        return

    def _create_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_create` """
        return map_record.values(for_create=True, fields=fields, **kwargs)

    def _create(self, data):
        """ Create the external record """
        # special check on data before export
        self._validate_create_data(data)
        return self.backend_adapter.create(data)

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        return map_record.values(fields=fields, **kwargs)

    def _update(self, data):
        """ Update an external record """
        assert self.external_id
        # special check on data before export
        self._validate_update_data(data)
        self.backend_adapter.write(self.external_id, data)


class ExternalDeleter(AbstractComponent):
    """Base deleter for external source."""
    _name = 'external.exporter.deleter'
    _inherit = 'base.deleter'
    _usage = 'record.exporter.deleter'

    def run(self, external_id):
        """Run the synchronization and delete the record in external."""
        self.backend_adapter.delete(external_id)
        return 'Record {} deleted on external source'.format(external_id)
