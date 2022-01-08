var express = require("express");
var router = express.Router();
const USERS_SERVICE_ADDRESS = require('../../configs/config').USERS_SERVICE_ADDRESS;
var authorization = require('../../middlewares/authorization');

const axios = require('axios').default;

router.get("/:username", authorization.grantAccess("readOwn", "admin", "username"), async function (req, res, next) {
    let username = req.params.username;

    try {
        const resp = await axios.get(USERS_SERVICE_ADDRESS + `/admins/${username}`);
        // console.log(resp.data);
        res.json(resp.data);
    } catch (err) {
        console.error(err);
        res.json({ result: "error" });
    }
});

module.exports = { router };
