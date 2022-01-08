var express = require('express');
var router = express.Router();

router.use('/users', require('./users'))
router.use('/prescriptions', require('./prescriptions'))
router.use('/statistics', require('./statistics'))

module.exports = router;
