var express = require("express");
var router = express.Router();
var qs = require('qs');
const USERS_SERVICE_ADDRESS = require('../../configs/config').USERS_SERVICE_ADDRESS;
var authorization = require('../../middlewares/authorization');

const axios = require('axios').default;

router.post("/", authorization.grantAccess("createAny", "patient"), async function (req, res, next) {
    let name = req.body.name;
    let nationalCode = req.body.national_code;
    let password = req.body.password;

    try {
        const resp = await axios.post(USERS_SERVICE_ADDRESS + '/patients',
            qs.stringify({ name: name, national_code: nationalCode, password: password }));
        // console.log(resp.data);
        res.json(resp.data);
    } catch (err) {
        // console.error(err);
        res.json({ result: "error" });
        // res.render(err.data);
    }
});

router.get("/:nationalCode",
    authorization.grantAccessList(["readOwn", "readAny"], "patient", function ownCheck(req) {
        let resourceId = req.params["nationalCode"]
        return resourceId == (req.payload.user_type == "admin" ?
            req.payload.user_name : req.payload.national_code);
    }),
    async function (req, res, next) {
        let nationalCode = req.params.nationalCode;

        try {
            const resp = await axios.get(USERS_SERVICE_ADDRESS + `/patients/${nationalCode}`);
            // console.log(resp.data);
            res.json(resp.data);
        } catch (err) {
            console.error(err);
            res.json({ result: "error" });
        }
    });

router.get("/", authorization.grantAccess("readAny", "patient"), async function (req, res, next) {
    try {
        const resp = await axios.get(USERS_SERVICE_ADDRESS + '/patients', { params: req.query });
        // console.log(resp.data);
        res.json(resp.data);
    } catch (err) {
        console.error(err);
        res.json({ result: "error" });
    }
});

module.exports = { router };
