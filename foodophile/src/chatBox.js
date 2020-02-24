import React, { Component } from 'react'
import { Launcher } from 'react-chat-window'
import chatHistory from './chatHistory'

var apigClientFactory = require('aws-api-gateway-client').default;
var config = { invokeUrl: 'https://xz73cvumlc.execute-api.us-east-1.amazonaws.com/beta' }
var apigClient = apigClientFactory.newClient(config)
var pathParams = {
    userId: ''
}
var additionalParams = {
    //If there are query parameters or headers that need to be sent with the request you can add them here
    //headers: {
    //    param0: '',
    //   param1: ''
    //},
    //queryParams: {
    //    param0: '',
    //    param1: ''
    //}
};
var method = 'POST'
var pathTemplate = '/chatbot'
class chatBox extends Component {
    constructor(props) {
        super(props);
        this.state = {
            messageList: chatHistory,
            newMessagesCount: 2,
            isOpen: false,
        };
        this._onMessageWasSent = this._onMessageWasSent.bind(this);
        this._onFilesSelected = this._onFilesSelected.bind(this);
        this._handleClick = this._handleClick.bind(this);
        this._sendMessage = this._sendMessage.bind(this);
    }
    _onMessageWasSent(message) {
        var body = {
            messages: message.data['text']
        }

        apigClient.invokeApi(pathParams, pathTemplate, method, additionalParams, body)
            .then((result) => {
                var text = result.data.body
                text = text.substring(1, text.length - 1)
                this._sendMessage(text)
            }).catch(function (result) {
            });

        this.setState({
            messageList: [...this.state.messageList, message]
        })
    }

    _sendMessage(text) {
        if (text.length > 0) {
            this.setState({
                messageList: [...this.state.messageList, {
                    author: 'them',
                    type: 'text',
                    data: { text }
                }],
                newMessagesCount: this.state.newMessagesCount + 1
            })
        }
    }

    _onFilesSelected(fileList) {
        const objectURL = window.URL.createObjectURL(fileList[0]);
        this.setState({
            messageList: [...this.state.messageList, {
                type: 'file', author: 'me',
                data: {
                    url: objectURL,
                    fileName: fileList[0].name
                }
            }]
        });
    }

    _handleClick() {
        this.setState({
            isOpen: !this.state.isOpen,
            newMessagesCount: 0
        });
    }

    render() {
        return (<div>
            <Launcher
                agentProfile={{
                    teamName: 'Foodophile',
                    imageUrl: 'https://a.slack-edge.com/66f9/img/avatars-teams/ava_0001-34.png'
                }}
                onMessageWasSent={this._onMessageWasSent}
                messageList={this.state.messageList}
                onFilesSelected={this._onFilesSelected}
                newMessagesCount={this.state.newMessagesCount}
                handleClick={this._handleClick}
                isOpen={this.state.isOpen}
                showEmoji
            />
        </div>)
    }
}

export default chatBox;