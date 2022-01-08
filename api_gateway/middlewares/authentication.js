const urlsAccessPolicy = require("../configs/allowedUrls");
const JWT_SECRET = require('../configs/config').JWT_SECRET;
var _ = require("underscore");
var jwt = require('jsonwebtoken');

function authentication(req, res, next) {
    let authorization = req.headers.authorization;
    try {
        let token = authorization.split(' ')[1];
        let payload = jwt.verify(token, JWT_SECRET);
        req.payload = payload;
        next()
    } catch (error) {
        // console.log(error);
        // console.log("invalid access token");
        req.payload = {user_type: "basic"}
        next();
    }
}

module.exports = authentication;
