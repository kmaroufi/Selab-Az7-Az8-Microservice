var express = require("express");
var router = express.Router();
var qs = require('qs');
const STATISTICS_SERVICE_ADDRESS = require('../configs/config').STATISTICS_SERVICE_ADDRESS;
var authorization = require('../middlewares/authorization');

const axios = require('axios').default;

router.get("/:year/:month/:day",
    authorization.grantAccess("readAny", "statistic"), async function (req, res, next) {
        let year = req.params.year;
        let month = req.params.month;
        let day = req.params.day;

        try {
            const resp = await axios.get(STATISTICS_SERVICE_ADDRESS + `/statistics/${year}/${month}/${day}`);
            // console.log(resp.data);
            res.json(resp.data);
        } catch (err) {
            console.error(err);
            res.json({ result: "error" });
        }
    });

    module.exports = router;