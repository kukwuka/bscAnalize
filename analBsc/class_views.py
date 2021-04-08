from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Coalesce
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AddressInfo
from .models import Profile
from .serializers import ProfileListSerializer, AddressInfoSerializer


class ProfileListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        profile_list = Profile.objects.all()
        serializer = ProfileListSerializer(profile_list, many=True)
        # print(serializer.data)
        return Response(serializer.data)

    def post(self, request):
        profile = ProfileListSerializer(data=request.data)
        if profile.is_valid():
            profile.save()
            return Response(status=201)
        else:
            return Response(status=400)


class ProfileDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            profile_query = Profile.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(data={'err': f'Cant find profile with this id :{pk}'}, status=400)

        serializer = ProfileListSerializer(profile_query)
        # print(serializer.data)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            profile_query = Profile.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(data={'err': f'Cant find profile with this id :{pk}'}, status=400)

        request.data['blockchain_address'] = profile_query.blockchain_address
        request.data['external_id'] = profile_query.external_id
        request.data['user_name'] = profile_query.user_name

        profile = ProfileListSerializer(instance=profile_query, data=request.data)
        print(request.data)
        if profile.is_valid():
            profile.save()
            return Response(status=200)
        else:
            # print(profile.data)
            return Response(status=400)

    def delete(self, request, pk):
        try:
            profile_query = Profile.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(data={'err': f'Cant find profile with this id :{pk}'}, status=400)
        profile_query.delete()
        return Response('Item succsesfully delete!', status=200)


class AddressInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        AdressInfo = AddressInfo.objects.all().order_by(Coalesce(
            'sumOfDfxOfUser',
            'value_buy',
            'value_FromStack').desc())
        serializer = AddressInfoSerializer(AdressInfo, many=True)
        return Response(serializer.data)
