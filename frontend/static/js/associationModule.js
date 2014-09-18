var associationsModule = angular.module('associationsModule', ['ui.bootstrap.datetimepicker']);

associationsModule.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});

associationsModule.filter('startFrom', function () {
    return function (input, start) {
        start = +start;
        return input.slice(start);
    }
});

associationsModule.controller('associationsController', function ($scope, $http) {

    $scope.pageSize = 10;
    $scope.searchText = "";
    $scope.hasError = false;
    $scope.associations = [];
    $scope.currentPage = 0;

    $scope.numberOfPages = function () {
        return Math.ceil($scope.associations.length / $scope.pageSize);
    };

    var url = $location.absUrl();
    var url_split = url.split('/');
    var indexOfId = url_split.indexOf('associations') + 1;
    var associationId = url_split[indexOfId];
    var isInt = /^\d+$/;

    if (isInt.test(associationId)) {
        $http.get('/api/associations/').
            success(function (data) {
                $scope.associations = data.associations;
            }).error(function (data, status, headers, config) {
                $scope.errorMessage = "Veuillez nous excuser, notre site rencontre des difficultés techniques. Nous vous invitions à réessayer dans quelques minutes.";
            });
    } else {
// get association
    }

    $scope.showAssociation = function (association_id) {
        window.location = '/associations/' + association_id + '/';
    };
});