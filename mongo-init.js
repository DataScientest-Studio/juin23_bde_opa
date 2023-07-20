/* Careful here, any error will be silently discarded and the database created whatsoever */

db.createUser(
    {
        user: "user",
        pwd: "password",
        roles: [
            {
                role: "readWrite",
                db: "stock_market"
            }
        ]
    }
);

db.createCollection("historical", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            title: "Historical values validation",
            required: ["_id", "date", "close", "symbol"],
            properties: {
                _id: { "bsonType": "objectId" },
                date: {
                    bsonType: "date",
                    description: "'date' must be a date and is required"
                },
                symbol: {
                    bsonType: "string",
                    description: "'symbol' must be a string and is required"
                },
                close: {
                    bsonType: "double",
                    description: "'close' must be a double and is required"
                }
            },
            additionalProperties: false
        }
    }
})
db.createCollection("streaming")
