"""Core ETL components: schema, loaders, pipeline."""
from .schema import TABLE_SCHEMAS
from .loaders import MariaDBLoader
from .pipeline import AcquisitionPipeline

__all__ = ["TABLE_SCHEMAS", "MariaDBLoader", "AcquisitionPipeline"]
