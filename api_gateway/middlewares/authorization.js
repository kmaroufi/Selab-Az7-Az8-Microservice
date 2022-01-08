const AccessControl = require("accesscontrol");
const ac = new AccessControl();

ac.grant("basic")
    .createAny("patient")
    .createAny("doctor")
    .createAny("jwt")

ac.grant("patient")
    .extend("basic")
    .readOwn("patient")
    .readOwn("prescription")

ac.grant("doctor")
    .extend("basic")
    .readOwn("doctor")
    .readOwn("prescription")
    .createAny("prescription")

ac.grant("admin")
    .extend("basic")
    .readAny("patient")
    .readAny("doctor")
    .readAny("prescription")
    .readOwn("admin")
    .readAny("statistic")

ac.deny("admin")
    .createAny("prescription")

exports.ac = ac

exports.grantAccess = function (action, resource, resourceField, params = true) {
    return async (req, res, next) => {
        try {
            const permission = ac.can(req.payload.user_type)[action](resource);
            granted = permission.granted;
            if (action.includes("Own")) {
                let resourceId = params ? req.params[resourceField] : req.query[resourceField]
                granted &= resourceId == (req.payload.user_type == "admin" ?
                    req.payload.user_name : req.payload.national_code);
            }
            if (!granted) {
                return res.status(401).json({
                    error: "You don't have enough permission to perform this action"
                });
            }
            next()
        } catch (error) {
            next(error)
        }
    }
}

exports.grantAccessList = function (actions, resource, ownCheck) {
    return async (req, res, next) => {
        for (let i in actions) {
            let action = actions[i];
            try {
                const permission = ac.can(req.payload.user_type)[action](resource);
                granted = permission.granted;
                if (action.includes("Own")) {
                    granted &= ownCheck(req);
                }
                if (granted) {
                    next()
                    return;
                }
            } catch (error) {
                console.log(error);
            }
        }
        return res.status(401).json({
            error: "You don't have enough permission to perform this action"
        });
    }
}