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

db.createCollection("historical")
db.createCollection("streaming")
