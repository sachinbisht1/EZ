"""Check db and create, delete table."""
import yaml
from initializers.aws import DYNAMODB_RESOURCE
from initializers.logger import LOGGER
from constants.utilities_constants import DATABASE_DIR
from constants.error_messages.database import COULD_NOT_CREATE_TABLE
from botocore.exceptions import ClientError

import os


class DbChecker:
    """Check db and perform operation accodingly."""

    def __init__(self) -> None:
        """Initialize connection with dynamoDB."""
        self.dynmodb_resource = DYNAMODB_RESOURCE
        self.database_config_dir = os.path.join(os.getcwd(), DATABASE_DIR)
        self.tables = os.listdir(self.database_config_dir)
        print(f"{self.tables=}")

    def yaml_to_dict(self, table_config):
        """Convert yaml to dict."""
        table_config_path = os.path.join(self.database_config_dir, table_config)
        with open(table_config_path, "r") as config_data:
            configuration = yaml.safe_load(config_data)
        return configuration

    def check_pre_exist_tables(self):
        """Check any pre exist table."""
        existing_tables = list(self.dynmodb_resource.tables.all())
        print(f"{existing_tables=}")
        return [table.name for table in existing_tables]

    def tables_need_to_create(self):
        """Get table names need to create."""
        existing_tables = self.check_pre_exist_tables()
        for table in existing_tables:
            if f"{table}.yml" in self.tables:
                LOGGER.debug("Table already exist --> %s", table)
                self.tables.remove(f"{table}.yml")
            else:
                LOGGER.error("Table %s needs to delete, Delete it manually", table)
        for table_name in self.tables:
            if ".yml" not in table_name:
                self.tables.remove(table_name)
        return self.tables

    def create_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput, lsi=[]):
        """Create table on server."""
        try:
            if lsi:
                table = self.dynmodb_resource.create_table(
                    TableName=table_name,
                    KeySchema=key_schema,
                    AttributeDefinitions=attribute_definitions,
                    ProvisionedThroughput=provisioned_throughput,
                    LocalSecondaryIndexes=lsi)
            else:
                table = self.dynmodb_resource.create_table(
                    TableName=table_name,
                    KeySchema=key_schema,
                    AttributeDefinitions=attribute_definitions,
                    ProvisionedThroughput=provisioned_throughput)
            table.wait_until_exists()
            LOGGER.info("Table created --> %s", table_name)

        except ClientError as err:
            error_msg = COULD_NOT_CREATE_TABLE.format(table_name,
                                                      err.response['Error']['Code'], err.response['Error']['Message'])
            return error_msg

    def execute(self):
        """Create and delete required tables."""
        print("executing")
        creating_tables_list = self.tables_need_to_create() or []
        failed_tables = []
        new_table_created = []
        for table in creating_tables_list:
            if "columns" in str(table):
                continue
            try:
                configuration = self.yaml_to_dict(table)
                print(f"{configuration=}")
                self.create_table(table_name=configuration["TableName"], key_schema=configuration["KeySchema"],
                                  attribute_definitions=configuration["AttributeDefinitions"],
                                  provisioned_throughput=configuration["ProvisionedThroughput"],
                                  lsi=configuration.get('LocalSecondaryIndexes', []) or [])
                new_table_created.append(configuration["TableName"])
            except Exception as ex:
                LOGGER.error("Table --> %s failed to create", table)
                LOGGER.error("Error --> %s", ex.args)
                failed_tables.append(table)
        return {"creating_tables_list": creating_tables_list,
                "failed_tables": failed_tables,
                "new_table_created": new_table_created}
