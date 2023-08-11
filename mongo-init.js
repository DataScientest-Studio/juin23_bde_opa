/* Careful here, any error will be silently discarded and the database created whatsoever */

const username = fs.readFileSync("/run/secrets/mongodb_username").toString().trim()
const password = fs.readFileSync("/run/secrets/mongodb_password").toString().trim()

db.createUser(
    {
        user: username,
        pwd: password,
        roles: [{ role: "readWrite", db: "stock_market" },
                { role: "readWrite", db: "stock_market-dev" },
                { role: "readWrite", db: "stock_market-test" }]
    }
);
