angular.module('alertList')
  .controller('TicketListController', function CheckoutCartController($scope, $websocket, $window, localStorageService) {
    $scope.allMessages = localStorageService.get('allMessages') ? localStorageService.get('allMessages') : [];
    $scope.highPriority = [];
    $scope.mediumPriority = [];
    $scope.lowPriority = [];

    $window.onbeforeunload = function() {
      localStorageService.set('allMessages', $scope.allMessages);
    }

    var dataStream = $websocket('ws://192.168.4.56:23456');
    dataStream.onMessage(function(message) {
      console.log(message.data);
      $scope.allMessages.push(JSON.parse(message.data));
      sortByPriority();
    });

    function sortByPriority() {
      var categorizedGroup = _.groupBy($scope.allMessages, 'priority');
      $scope.highPriority = categorizedGroup['HIGH'];
      $scope.mediumPriority = categorizedGroup['MEDIUM'];
      $scope.lowPriority = categorizedGroup['LOW'];
    }

    $scope.removeItem = function(id) {
      $scope.allMessages = _.filter($scope.allMessages, function(message) {
        return message._id != id;
      });
      sortByPriority();
    }
    sortByPriority();
  }
);
