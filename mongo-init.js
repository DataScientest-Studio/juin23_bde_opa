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
            required: ["_id", "date", "close", "ticker"],
            properties: {
                _id: { "bsonType": "objectId" },
                date: {
                    bsonType: "date",
                    description: "'date' must be a date and is required"
                },
                ticker: {
                    bsonType: "string",
                    description: "'ticker' must be a string and is required"
                },
                close: {
                    bsonType: "double",
                    description: "'close' must be a double and is required"
                },
                open: {
                    bsonType: "double",
                    description: "'open' must be a double if present"
                },
                low: {
                    bsonType: "double",
                    description: "'low' must be a double if present"
                },
                high: {
                    bsonType: "double",
                    description: "'high' must be a double if present"
                },
                volume: {
                    bsonType: "int",
                    description: "'volume' must be an int if present"
                }
            },
            additionalProperties: false
        }
    }
})
db.createCollection("streaming")
db.createCollection("company_info")

db.historical.createIndex( { "date": 1, "ticker": 1 }, { unique: true } )
