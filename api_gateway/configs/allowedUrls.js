const urlsAccessPolicy = {
    patient: [
        "/users/patients"
    ],
    doctor: [
        "/users/doctors",
        "/prescriptions"
    ],
    admin: [
       "/users/patients",
       "/users/doctors",
       "/admins",
       "/prescriptions" 
    ],
    other: [
        "/users/auth"
    ]
}

module.exports = urlsAccessPolicy;
