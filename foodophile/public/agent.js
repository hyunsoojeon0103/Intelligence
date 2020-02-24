var apigClient = apigClientFactory.newClient()
var body = {
    messages: [{ type: 'string' }]
}
var res = apigClient.chatbotPost({}, body, {}).then(function (result) {
    console.log(result);
}).catch(function (result) { });