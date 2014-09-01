var bidsModule = angular.module('bidsModule', []);
    $scope.technicalError = "Veuillez nous excuser, notre site rencontre des difficultés techniques. Nous vous invitions à réessayer dans quelques minutes.";
bidsModule.filter('startFrom', function () {
    return function (input, start) {
        start = +start; //parse to int

        return input.slice(start);
    }
});


bidsModule.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});

bidsModule.controller('bidsController', function ($scope, $http) {

    $scope.pageSize = 10;
    $scope.searchText = "";
    $scope.hasError = false;
    $scope.bids = [];
    $scope.currentPage = 0;
    $scope.getBids = function () {
        $http.get('/api/bids/').
            success(function (data) {
                $scope.bids = data.bids;
            }).error(function () {
                $scope.errorMessage = $scope.technicalError;
            });
    };
    $scope.getBids();

    $scope.numberOfPages = function () {
        return Math.ceil($scope.bids.length / $scope.pageSize);
    };

    $scope.showBid = function (element) {

        window.location = '/annonces/' + element.bid.id + '/';

    };
});

bidsModule.controller('createBidController', function ($scope, $http) {
    $scope.form_title = "Création d'une annonce";
    $scope.bid = {};

    $scope.getCategories = function () {
        $http.get('/api/categories/').
            success(function (data) {
                $scope.categories = data.categories;
            }).error(function () {
                $scope.errorMessage = $scope.technicalError;
            });
    };

    $scope.createBid = function () {
        if ($scope.bid.title.length == 0 || $scope.bid.description.length == 0) {
            $scope.errorMessage = "Le titre et la description d'une annonce doivent être renseignés";
        } else {
            $http.post('/api/bids/', $scope.bid).
                success(function (data, status, headers, config) {
                    window.location = '/annonces/' + data['bid_id'] + '/';
                }).error(function (data, status, headers, config) {
                    $scope.errorMessage = $scope.technicalError;
                });
        }
    };
});


bidsModule.controller('bidController', function ($scope, $http, $location) {
    $scope.hasError = false;
    $scope.bid = [];

    $scope.user_id = "";
    $scope.bid_id = "";
    $scope.form_title = "Modification d'une annonce";
    $scope.getidBid = function (url) {
        var url_split = url.split('/');
        var indexOfId = url_split.indexOf('annonces') + 1;
        return url_split[indexOfId];
    };

    $scope.idBid = $scope.getidBid($location.absUrl());

    $scope.getBid = function () {
        $http.get('/api/bids/' + $scope.idBid + '/').
            success(function (data) {
                $scope.bid = data.bids;
            }).error(function () {
                $scope.errorMessage = $scope.technicalError;
            });
    };
    $scope.getBid();

    $scope.acceptBid = function () {
        $http.put('/api/bids/' + $scope.idBid + '/accept/').
            success(function (data, status, headers, config) {
                $scope.successMessage = "Vous avez accepté cette annonce";
            }).error(function (data, status, headers, config) {
                $scope.errorMessage = $scope.technicalError;
            });
    };

});