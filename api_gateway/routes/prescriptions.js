var express = require("express");
var router = express.Router();
var qs = require('qs');
var authorization = require('../middlewares/authorization');
const PRESCRIPTIONS_SERVICE_ADDRESS = require('../configs/config').PRESCRIPTIONS_SERVICE_ADDRESS;
const PRESCRIPTIONS_VIEW_SERVICE_ADDRESS = require('../configs/config').PRESCRIPTIONS_VIEW_SERVICE_ADDRESS;

const axios = require('axios').default;

router.post("/", authorization.grantAccess("createAny", "prescription"), async function (req, res, next) {
    let patientNationalCode = req.body.patient_national_code;
    let doctorNationalCode = req.payload.national_code;
    let drugList = req.body.drug_list;
    let comment = req.body.comment;

    try {
        const resp = await axios.post(PRESCRIPTIONS_SERVICE_ADDRESS + '/prescriptions', 
            qs.stringify({patient_national_code: patientNationalCode, 
                doctor_national_code: doctorNationalCode, 
                drug_list: drugList, 
                comment: comment}));
        console.log(resp.data);
        res.json(resp.data);
    } catch (err) {
        console.error(err);
        res.json({ isSignedUp: false });
    }
});

router.get("/", authorization.grantAccessList(["readOwn", "readAny"], "prescription", ownCheck), async function (req, res, next) {
    try {
        const resp = await axios.get(PRESCRIPTIONS_VIEW_SERVICE_ADDRESS + '/prescriptions', { 
            params: req.query
        });
        console.log(resp.data);
        res.json(resp.data);
    } catch (err) {
        console.error(err);
        res.json({ isSignedUp: false });
    }
});

function ownCheck(req) {
    return req.payload.user_type == req.query.for &&
        req.query.national_code == req.payload.national_code;
}

module.exports = router;
