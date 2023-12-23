from rest_framework import generics, response, status
from .serializers import UserLoginSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    authentication_classes = []

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        access = TokenObtainPairSerializer.get_token(
            serializer.validated_data.get("user")
        )
        if not access:
            return response.Response(
                {"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

        return response.Response(
            {"access": str(access.access_token)}, status=status.HTTP_200_OK
        )
