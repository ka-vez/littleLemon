from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.paginator import EmptyPage, Paginator
from django.contrib.auth.models import User, Group

from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer
from .throttle import TenCallsPerMinute


# Create your views here.
@api_view(['POST', 'DELETE'])
@permission_classes([IsAdminUser])
def manager(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        if request.method == 'POST':
            managers.user_set.add(user)
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
        return Response({'message': 'ok'})
    else:
        return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)   


@api_view()
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def throttle_check(request):
    return Response({"message": "sucessful"})

@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    return Response({"message": "sucessful for logged in users only"})

@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category,pk=pk)
    serialized_category = CategorySerializer(category)
    return Response(serialized_category.data) 

@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        searched = request.query_params.get('searched')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        if category_name:
            items = items.filter(category__slug=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if searched:
            items = items.filter(title__contains=searched)
        if ordering:
            ordering_fields = ordering.split(',')
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    
    if request.method == 'POST':
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        print(serialized_item.validated_data)
        serialized_item.save()
        return Response(serialized_item.data, 201)

@api_view(['GET', 'PATCH', 'DELETE'])
def single_item(request, id):
    if request.method == "GET":
        item = get_object_or_404(MenuItem, pk=id)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    
    if request.method == 'PATCH':
        item = MenuItem.objects.filter(pk=id)
        menu_item = get_object_or_404(MenuItem, pk=id)
        price = request.query_params.get('price')
        item.update(price=price)
        return Response({'Updated the price of' : menu_item.title })
    
    if request.method == 'DELETE': 
        item = get_object_or_404(MenuItem, pk=id)
        serialized_item = MenuItemSerializer(item)
        item.delete()
        return Response({'deleted' : item.title})


@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({'message': f'This is a secret message for {request.user.username}'})

@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name="Manager").exists():
        return Response({'message': f'This is a secret message for Manager {request.user.username}'})
    else:
        return Response({'message': f'You are not a manager {request.user.username}'}, 403)

# class MenuItemsView(generics.ListCreateAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     ordering_fields = ['title']

# class SingleItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer

