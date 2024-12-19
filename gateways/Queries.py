"""All dynamodb queries."""
from initializers.aws import DYNAMODB_CLIENT
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from controllers.utilities import generate_uuid

update_expression = "UpdateExpression"
expression_attribute_name = "ExpressionAttributeNames"
expression_attribute_value = "ExpressionAttributeValues"
transaction_values = "transaction_values"


class Queries:
    """All Dynamodb queries."""

    def __init__(self) -> None:
        """Initialize connection with dynamodb."""
        self.dynamodb_client = DYNAMODB_CLIENT
        self.deserializer = TypeDeserializer().deserialize
        self.serializer = TypeSerializer().serialize

    def from_dynamodb_to_json(self, item):
        """Convert dynamo-json to dict."""
        simplified_item = {}

        for key, value in item.items():
            # print(f"{type(value)=}")
            simplified_item[key] = self.deserializer(value=value)
        simplified_item = {key: self.deserializer(value=value) for key, value in item.items()}

        return simplified_item

    def dynmodb_key_generator(self, item: dict):
        """Generate key in dynamodb json format."""
        dynamodb_key = {}
        for key, value in item.items():
            if isinstance(value, float):
                value = str(value)
            dynamodb_key[key] = self.serializer(value=value)
        return dynamodb_key

    def get_item(self, table_name: str, key: dict, required_attributes: list = []) -> dict:
        """Query to get item from dynamodb."""
        if not required_attributes:
            response = self.dynamodb_client.get_item(TableName=table_name, Key=self.dynmodb_key_generator(key))
        else:
            response = self.dynamodb_client.get_item(TableName=table_name,
                                                     Key=self.dynmodb_key_generator(key),
                                                     AttributesToGet=required_attributes)
        if response.get("Item"):
            item = self.from_dynamodb_to_json(response.get("Item"))
            item["found"] = True
            return item
        else:
            return {}

    def get_item_by_partition_key(self, table_name: str, partiotion_key: str, value: str,
                                  required_attributes: list = [], multiple=False):
        """Query to get item using only partition key."""
        if required_attributes:
            required_attributes = ", ".join(required_attributes)
            print(f"{required_attributes=}")
            response = self.dynamodb_client.query(
                TableName=table_name,
                Select='SPECIFIC_ATTRIBUTES',
                ProjectionExpression=required_attributes,
                ExpressionAttributeValues={
                    ':v1':  {
                        "S": value
                    }
                },
                KeyConditionExpression=f'{partiotion_key} = :v1',
                )
        else:
            response = self.dynamodb_client.query(
                TableName=table_name,
                ExpressionAttributeValues={
                    ':v1':  {
                        "S": value
                    }
                },
                KeyConditionExpression=f'{partiotion_key} = :v1'
                )

        if response.get("Items") and not multiple:
            return self.from_dynamodb_to_json(response.get("Items")[0])
        elif response.get("Items") and multiple:
            items = response.get("Items")
            response = []
            for each_item in items:
                response.append(self.from_dynamodb_to_json(each_item))
            return response
        else:
            return {}

    def generate_dynamodb_updaters(self, values_to_update: dict):
        """Generate expression to update data on dynamodb."""
        generated_attribute_names = []
        expression_attribute_name = {}
        expression_attribute_values = {}
        update_expression = "SET "

        for key, value in values_to_update.items():
            attr_name = f"#{key[0].upper()}"
            if attr_name in generated_attribute_names:
                attr_name = f"{attr_name}{generate_uuid()}"
            generated_attribute_names.append(attr_name)
            expression_attribute_name[attr_name] = key

            attr_value = f":{attr_name[1:].lower()}value"
            if isinstance(value, float):
                value = str(value)
            serialized_value = self.serializer(value=value)

            expression_attribute_values[attr_value] = serialized_value

            update_expression += f"{attr_name} = {attr_value}, "
        update_expression = update_expression[:-2]

        return {"ExpressionAttributeNames": expression_attribute_name,
                "ExpressionAttributeValues": expression_attribute_values,
                "UpdateExpression": update_expression}

    def generate_dynamodb_getters(self, values_to_get: dict, condition: str):
        """Generate expression to update data on dynamodb. Condition options --> [=, >, <, >=, <=]."""
        generated_attribute_names = []
        expression_attribute_name = {}
        expression_attribute_values = {}
        get_expression = ""

        for key, value in values_to_get.items():
            attr_name = f"#{key[0].upper()}"
            if attr_name in generated_attribute_names:
                attr_name = f"#{attr_name}{generate_uuid()}"
            generated_attribute_names.append(attr_name)
            expression_attribute_name[attr_name] = key

            attr_value = f":{attr_name[1:].lower()}value"
            if isinstance(value, float):
                value = str(value)
            serialized_value = self.serializer(value=value)

            expression_attribute_values[attr_value] = serialized_value
            if not get_expression:
                get_expression = f"{attr_name} = {attr_value}"
            else:
                get_expression += f" AND {attr_name} = {attr_value}"

        return {"ExpressionAttributeNames": expression_attribute_name,
                "ExpressionAttributeValues": expression_attribute_values,
                "GetExpression": get_expression}

    def update_item(self, table_name: str, key: dict, values_to_update: dict):
        """Query to update dynamodb item."""
        updater_helper = self.generate_dynamodb_updaters(values_to_update=values_to_update)
        print(f"{updater_helper=}")
        self.dynamodb_client.update_item(
            ExpressionAttributeNames=updater_helper[expression_attribute_name],
            ExpressionAttributeValues=updater_helper[expression_attribute_value],
            Key=self.dynmodb_key_generator(key),
            ReturnValues='ALL_NEW',
            TableName=table_name,
            UpdateExpression=updater_helper[update_expression],
        )
        return {"UPDATED": True}

    def get_all_items(self, table_name):
        """Get all table items."""
        all_data = self.dynamodb_client.scan(TableName=table_name)
        all_items = all_data.get("Items")
        simplified_all_items = [self.from_dynamodb_to_json(item) for item in all_items]
        return simplified_all_items

    def get_batch_items(self, table_name, partition_key, partition_key_values: list, required_attributes: list = []):
        """Get different multiple items from database."""
        dynamo_partition_keys = []
        for each in partition_key_values:
            dynamo_partition_keys.append(self.dynmodb_key_generator({partition_key: each}))
        request_item = {
            'Keys': dynamo_partition_keys,
        }

        if required_attributes:
            request_item["AttributesToGet"] = required_attributes
        response = self.dynamodb_client.batch_get_item(
            RequestItems={
                table_name: request_item
            }
        )
        responses = response.get('Responses', {}).get(table_name) or {}
        parsed_response = []
        if responses and len(responses) > 1:
            for each_item in responses:
                parsed_response.append(self.from_dynamodb_to_json(item=each_item))
            return parsed_response
        elif responses:
            return self.from_dynamodb_to_json(item=responses[0])
        return response or {}

    def delete_item(self, table_name: str, keys: str, multiple=False):
        """Query to get item using only partition key."""
        keys = self.dynmodb_key_generator(keys)
        print(f"{keys=}")
        response = self.dynamodb_client.delete_item(
            TableName=table_name,
            Key=keys)
        return response or {}
