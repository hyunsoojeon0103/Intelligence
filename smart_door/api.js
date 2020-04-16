/* This function has been moved to wp1.html*/
/* function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
	results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}*/
function isValidFaceId(faceId) {
    var reg = /^[a-zA-Z0-9]{8}(-[a-zA-Z0-9]{4}){3}-[a-zA-Z0-9]{12}$/
    if (faceId.match(reg))
	return true;
    return false;
}
function isValidName(name) {
    var reg = /^[a-zA-Z]+[a-zA-Z ]*$/;
    if (name.match(reg))
	return true;
    return false;
}
function isValidPhoneNumber(number) {
    var reg = /^[0-9]{10}$/;
    if (number.match(reg))
	return true;
    return false;
}
function submitForm() {
    var faceId = document.getElementById("faceId").value;
    var nickname = document.getElementById("nickname").value;
    var phoneNumber = document.getElementById("phoneNumber").value;
    if (isValidFaceId(faceId) && isValidName(nickname) && isValidPhoneNumber(phoneNumber)) {
        phoneNumber = '+1' + phoneNumber;
        var apigClient = apigClientFactory.newClient();
        var body = {
            faceId: faceId,
            nickname: nickname,
            phoneNumber: phoneNumber
	    }
        var res = apigClient.registerPost({}, body, {}).then(function (result) {
        }).catch(function (result) {});
    }
}
function submitOTP() {

    var OTP = document.getElementById("OTP").value;
    var apigClient = apigClientFactory.newClient();
    var body = {
        otp: OTP
    }
    var res = apigClient.checkPWDPost({}, body, {}).then(function (result) {
        if (result['data'] == "permission denied!")
            alert(result['data']);
        else
            alert(result['data']);
        window.location.href = "wp2.html";
    }).catch(function (result) {});
}
