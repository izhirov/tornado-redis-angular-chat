angular.module('chatApplication', [
    'ngWebSocket',
    'angular-jwt'
]).config(['$interpolateProvider','$httpProvider', function($interpolateProvider, $httpProvider) {
  $interpolateProvider.startSymbol('{*');
  $interpolateProvider.endSymbol('*}');
  $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
}]).
    constant('ServerConstant', {
        usersURL: location.origin.replace(/^http/, 'ws') + '/ws/users/',
        chatURL: location.origin.replace(/^http/, 'ws') + '/ws/chat/',
        chatHTTPURL: location.origin,
        authURL: location.origin + '/api/auth/',
        registerURL: location.origin + '/api/register/'
    })
    .service('AuthService', AuthService)
    .factory('Users', Users)
    .factory('UserData', UserData)
    .factory('Messages', Messages)
    .factory('MessageEntity', MessageEntity)

.controller('ChatController', ChatController);

// todo: Refactor many stuff here.
function ChatController($scope, Users, UserData, AuthService, Messages, MessageEntity, $http, ServerConstant) {
    $scope.activeState = 'auth';
    $scope.users = new Users();
    $scope.userData = new UserData();
    $scope.messages = Messages;
    $scope.messageData = new MessageEntity();

    $scope.register = function () {
        AuthService.register($scope.userData).then(function () {
            $scope.userData = new UserData();
            $scope.activeState = 'authorized';
            $scope.users.openSocket();
            $scope.messages.socketOpen();
        }, function (error) {
            alert(JSON.stringify(error));
        });
    };

    $scope.auth = function () {
        AuthService.auth($scope.userData).then(function () {
            $scope.userData = new UserData();
            $scope.activeState = 'authorized';
            $scope.users.openSocket();
            $scope.messages.socketOpen();
        }, function (error) {
            alert(JSON.stringify(error));
        });
    };

    $scope.prepareMessage = function (email_to) {
        $scope.messageData.to = email_to;
    };

    $scope.sendMessage = function (keyEvent) {
        if(keyEvent && keyEvent.which !== 13)
            return;

        $scope.messageData.from = AuthService.getCurrentUser().email;
        $http.post(ServerConstant.chatHTTPURL, $.param($scope.messageData)).then(function () {
            $scope.messageData = new MessageEntity();
        });
    };
}

function Users($websocket, ServerConstant, AuthService) {
    function UsersWrapper() {
        this.data = [];
        this.dataStream = "";
    }
    UsersWrapper.prototype.openSocket = function () {
        var self = this;
        var user = AuthService.getCurrentUser();
        self.dataStream = $websocket(ServerConstant.usersURL + user.token);
        self.dataStream.onMessage(function(message) {
            if(message.data)
                self.data = JSON.parse(message.data)
        });
    };
    return UsersWrapper;
}

function UserData() {
    function UserWrapper() {
        this.first_name = '';
        this.last_name = '';
        this.email = '';
        this.password = '';
    }
    return UserWrapper;
}

function Messages($websocket, ServerConstant, AuthService) {
    var data = [];
    function socketOpen() {
        var user = AuthService.getCurrentUser();
        var dataStream = $websocket(ServerConstant.chatURL + user.token);
        dataStream.onMessage(function(message) {
            if(message.data)
                data.unshift(JSON.parse(message.data));
        });
    }
    return {
        data: data,
        socketOpen: socketOpen
    }
}

function AuthService($http, $q, ServerConstant) {
    var currentUser = {};

    function server_post(url, data) {
        var defer = $q.defer();
        $http.post(url, $.param(data)).then(function (result) {
            currentUser = result.data;
            defer.resolve(result.data);
        }, function (error) {
            defer.reject(error.data);
        });
        return defer.promise;
    }
    return {
        getCurrentUser: function () {
            return currentUser;
        },
        auth: function (data) {
            return server_post(ServerConstant.authURL, data);
        },
        register: function (data) {
            return server_post(ServerConstant.registerURL, data);
        }
    }
}

function MessageEntity() {
    function MessageEntityWrapper() {
        this.text = "";
        this.from = "";
        this.to = "";
    }
    return MessageEntityWrapper;
}
