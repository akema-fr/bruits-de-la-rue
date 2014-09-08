# coding=utf-8
import json

from django.http.response import HttpResponse, HttpResponseForbidden

from api.decorators import b2rue_authenticated as is_authenticated
from api.decorators import catch_any_unexpected_exception
from api.errors import error_codes
from api.http_response import HttpMethodNotAllowed, HttpCreated, HttpBadRequest, HttpNoContent
from api.validators import BidValidator
from core.models import Bid, BidCategory, Address, User, Association


def get_bids(request):
    bids = Bid.objects.filter(status="RUNNING")
    return_bids = []
    if bids:
        for bid in bids:
            return_bids.append(bid.serialize())
    return HttpResponse(json.dumps({'bids': return_bids}), content_type='application/json')


def clean_dict(dict):
    """
    :param dict: 
    :return: The dict containing only fields with values.
    """
    cleaned_dict = {}
    for key, value in dict.items():
        if value:
            cleaned_dict[key] = value
    return cleaned_dict


# Todo : Explode / Refactor ..
def create_bid(request):
    bid_cleaned = clean_dict(json.loads(request.body))
    if bid_cleaned:
        bid_validator = BidValidator()
        if bid_validator.bid_is_valid(bid_cleaned):
            bid_cleaned['creator'] = request.user
            if 'localization' in bid_cleaned:
                bid_cleaned['localization'] = Address.objects.get(
                    id=bid_cleaned['localization']['id'])
            if 'association' in bid_cleaned:
                bid_cleaned['association'] = Association.objects.get(id=bid_cleaned['association']['id'])

            if 'category' in bid_cleaned:
                bid_cleaned['category'], created = BidCategory.objects.get_or_create(
                    name=bid_cleaned['category']['name'])
            if 'begin' in bid_cleaned and 'end' in bid_cleaned:
                if bid_cleaned['begin'] > bid_cleaned['end']:
                    return HttpBadRequest(10215, error_codes['10215'])
        new_bid = Bid(**bid_cleaned)
        new_bid.save()
        new_bid_id = new_bid.id
        return HttpCreated(json.dumps({'bid_id': new_bid_id}), location='/api/bids/%d/' % new_bid_id)
    return HttpBadRequest(10900, error_codes['10900'])


def get_bid(request, bid_id):
    bids = Bid.objects.filter(id=bid_id)
    if bids:
        serialize = bids[0].serialize()
        serialize['current_user_id'] = request.user.id
        serialize['current_user_is_staff'] = request.user.is_staff
        return HttpResponse(json.dumps(serialize), content_type='application/json')


def accept_bid_that_have_a_quantity(bid_dict, matching_bid, user):
    if 0 < bid_dict['quantity'] <= matching_bid.quantity:
        matching_bid.quantity = matching_bid.quantity - bid_dict['quantity']
    else:
        return HttpBadRequest(10218, error_codes['10218'])
    matching_bid.purchaser = user
    if matching_bid.quantity == 0:
        matching_bid.status = "ACCEPTED"
    matching_bid.save()
    return HttpResponse()


def handle_accept_bid(request, bid_dict, matching_bid):
    user = request.user
    if user != matching_bid.creator and matching_bid.status == "RUNNING":
        if 'quantity' in bid_dict:
            return accept_bid_that_have_a_quantity(bid_dict, matching_bid, user)
        else:
            matching_bid.purchaser = user
            matching_bid.status = "ACCEPTED"
            matching_bid.save()
            return HttpResponse()
    return HttpBadRequest(10217, error_codes['10217'])


# todo pop in validator
def bid_dict_clean(bid_dict):
    bid_dict.pop('creator', None)
    bid_dict.pop('current_user_is_staff', None)
    bid_dict.pop('current_user_id', None)
    if 'localization' in bid_dict:
        bid_dict['localization'] = Address.objects.get(id=bid_dict['localization']['id'])
    if 'category' in bid_dict:
        bid_dict['category'] = BidCategory.objects.get(id=bid_dict['category']['id'])
    return bid_dict


def update_bid(request, bid_id):
    bid_dict = clean_dict(json.loads(request.body))
    matching_bid = Bid.objects.filter(id=bid_dict['id'])
    bid_validator = BidValidator()
    if matching_bid and bid_dict:
        bid_dict_clean(bid_dict)
        bid = matching_bid[0]
        if 'status' in bid_dict and bid_dict['status'] == 'ACCEPTED' and bid.status != "ACCEPTED":
            return handle_accept_bid(request, bid_dict, bid)
        if bid.creator == request.user or request.user.is_staff:
            if bid_validator.bid_is_valid(bid_dict):
                matching_bid.update(**bid_dict)
                return HttpResponse()
            else:
                return HttpBadRequest(10666, error_codes['10666'])
    return HttpBadRequest(10216, error_codes['10216'])


@is_authenticated
@catch_any_unexpected_exception
def handle_bids(request):
    if request.method == "GET":
        return get_bids(request)

    if request.method == "POST":
        return create_bid(request)
    return HttpMethodNotAllowed()


def delete_bid(request, bid_id):
    bids = Bid.objects.filter(id=bid_id)
    if bids:
        bid = bids[0]
        if bid.creator == request.user or request.user.is_staff:
            bid.delete()
            return HttpNoContent()
        return HttpResponseForbidden()
    return HttpBadRequest


@is_authenticated
@catch_any_unexpected_exception
def handle_bid(request, bid_id):
    if request.method == 'GET':
        return get_bid(request, bid_id)
    if request.method == 'PUT':
        return update_bid(request, bid_id)
    if request.method == 'DELETE':
        return delete_bid(request, bid_id)
    return HttpMethodNotAllowed()


def get_available_categories(request):
    categories = BidCategory.objects.all()
    return_categories = []
    if categories:
        for category in categories:
            return_categories.append(category.serialize())
    return HttpResponse(json.dumps({'categories': return_categories}), content_type='application/json')


@is_authenticated
@catch_any_unexpected_exception
def handle_categories(request):
    if request.method == "GET":
        return get_available_categories(request)
    return HttpMethodNotAllowed()


@is_authenticated
@catch_any_unexpected_exception
def get_current_user_username(request):
    return HttpResponse(request.user.username, content_type='application/json')


def create_new_address(request, user_id):
    new_address_infos = clean_dict(json.loads(request.body))
    user = User.objects.filter(id=user_id).select_related('address')
    if new_address_infos and user:
        new_address = Address(**new_address_infos)
        new_address.save()
        user[0].address.add(new_address)
        return HttpCreated()

    return HttpBadRequest(10900, error_codes['10900'])


@is_authenticated
@catch_any_unexpected_exception
def handle_address(request):
    if request.method == "GET":
        return get_current_user_address(request)
    if request.method == "POST":
        return create_new_address(request, request.user.id)
    return HttpMethodNotAllowed()


def get_current_user_address(request):
    address = Address.objects.filter(user=request.user)
    return_address = []
    if address:
        for a in address:
            return_address.append(a.serialize())
    return HttpResponse(json.dumps({'address': return_address}), content_type='application/json')


def get_current_user_associations(request):
    associations = Association.objects.filter(user=request.user)
    return_associations = []
    if associations:
        for a in associations:
            return_associations.append(a.serialize())
    return HttpResponse(json.dumps({'associations': return_associations}), content_type='application/json')

@is_authenticated
@catch_any_unexpected_exception
def handle_associations(request):
    if request.method == "GET":
        return get_current_user_associations(request)
    return HttpMethodNotAllowed()