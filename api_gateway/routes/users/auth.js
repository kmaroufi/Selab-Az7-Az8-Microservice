var express = require("express");
var router = express.Router();
var qs = require('qs');
const USERS_SERVICE_ADDRESS = require('../../configs/config').USERS_SERVICE_ADDRESS;
var authorization = require('../../middlewares/authorization');

const axios = require('axios').default;

router.post("/", authorization.grantAccess("createAny", "jwt"), async function(req, res, next) {
    let authorization = req.headers.authorization;
    let userType = req.query.userType;

    try {
        const resp = await axios.post(USERS_SERVICE_ADDRESS + `/auth?userType=${userType}`, 
        {},
        {
            "headers": {
                'User-Authorization': authorization
            }
        });
        res.json(resp.data);
    } catch (err) {
        console.error(err);
        res.json({ message: "server error" });
    }
});

module.exports = { router };