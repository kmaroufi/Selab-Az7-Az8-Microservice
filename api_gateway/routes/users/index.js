var express = require('express');
var router = express.Router();

router.use('/admins',require('./admins').router)
router.use('/doctors',require('./doctors').router)
router.use('/patients',require('./patients').router)
router.use('/auth',require('./auth').router)

module.exports = router;