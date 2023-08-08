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
