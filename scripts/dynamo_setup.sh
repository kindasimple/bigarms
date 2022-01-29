ENDPOINT_URL=${ENDPOINT_URL:-http://localhost:8888}

KEY_SCHEMA="AttributeName=member_id,KeyType=HASH AttributeName=time_created,KeyType=RANGE"

# Create local-entry table
aws dynamodb create-table \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-entry \
    --attribute-definitions \
        AttributeName=member_id,AttributeType=S \
        AttributeName=time_created,AttributeType=N \
    --key-schema AttributeName=member_id,KeyType=HASH AttributeName=time_created,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

echo "Create actionlog-tables-statistics"
aws dynamodb create-table \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-statistics \
    --attribute-definitions \
        AttributeName=member_id,AttributeType=S \
        AttributeName=action,AttributeType=S \
        AttributeName=entry_count,AttributeType=N \
        AttributeName=time_updated,AttributeType=N \
    --key-schema AttributeName=member_id,KeyType=HASH AttributeName=action,KeyType=RANGE \
    --global-secondary-indexes \
    "[
        {
            \"IndexName\": \"member-updated-index\",
            \"KeySchema\": [{\"AttributeName\":\"member_id\",\"KeyType\":\"HASH\"},
                            {\"AttributeName\":\"time_updated\",\"KeyType\":\"RANGE\"}],
            \"Projection\":{
                \"ProjectionType\":\"ALL\"
            }
        },
        {
            \"IndexName\": \"action-updated-index\",
            \"KeySchema\": [{\"AttributeName\":\"member_id\",\"KeyType\":\"HASH\"},
                            {\"AttributeName\":\"entry_count\",\"KeyType\":\"RANGE\"}],
            \"Projection\":{
                \"ProjectionType\":\"ALL\"
            }
        }
    ]" \
    --billing-mode PAY_PER_REQUEST

echo "Add items to actionlog-tables-statistics"

aws dynamodb put-item \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-statistics \
    --item \
        '{"member_id": {"S": "+16072152471"}, "action": {"S": "pushups"}, "entry_count": {"N": "10"}, "time_updated": {"N": "1619829907"}}'

aws dynamodb get-item \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-statistics \
    --key '{"member_id": {"S": "+6072152471"}, "action": {"S": "pushups"}}'

echo "Add items to actionlog-tables-entry"

aws dynamodb put-item \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-entry \
    --item \
            '{"member_id": {"S": "+16072152471"}, "time_created": {"N": "1619829907"}}'

aws dynamodb get-item \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-entry \
    --key '{"member_id": {"S": "+16072152471"}, "time_created": {"N": "1619829907"}}'

echo "Available tables:"

aws dynamodb \
    --endpoint-url $ENDPOINT_URL \
    list-tables

# aws dynamodb describe-table \
#     --endpoint-url $ENDPOINT_URL \
#     --table-name actionlog-tables-entry

aws dynamodb get-item \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-entry \
    --key '{"member_id": {"S": "+16072152471"}, "time_created": {"N": "1619829907"}}'

echo "Available Items:"

aws dynamodb query \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-entry \
    --key-condition-expression 'member_id = :a AND time_created BETWEEN :t1 AND :t2' \
    --expression-attribute-values '{
        ":a": {"S": "+16072152471"},
        ":t1": {"N": "1619829900"},
        ":t2": {"N": "1619829908"}
    }'

aws dynamodb query \
    --endpoint-url $ENDPOINT_URL \
    --table-name actionlog-tables-statistics \
    --key-condition-expression 'member_id = :a AND time_updated BETWEEN :t1 AND :t2' \
    --expression-attribute-values '{
        ":a": {"S": "+16072152471"},
        ":t1": {"N": "1619829900"},
        ":t2": {"N": "1619829908"}
    }'