'use strict';

// Declare app level module which depends on views, and components
angular.module('alertList', [
  'LocalStorageModule',
  'ngWebSocket',
  'ui.router'
]).
config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
  $stateProvider
    .state('main', {
      url: '',
      views:  {
        'content@': {
          templateUrl: 'templates/ticketList.html',
          controller: 'TicketListController'
        }
      }
    });

  // Send users to a 404 view by default

  $urlRouterProvider.otherwise('/404');

}]);
