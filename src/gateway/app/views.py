from rest_framework import views, response, status
from auth_svc import access
from pymongo import MongoClient
from config.settings import env
import gridfs

class LoginAPIView(views.APIView):
    def post(self, *args, **kwargs):
        token, err = access.login(self.request)
        if not err:
            return response.Response({"token": token}, status=status.HTTP_200_OK)
        else:
            return response.Response({"error": err}, status=status.HTTP_400_BAD_REQUEST)


class UploadAPIView(views.APIView):
    def post(self, *args, **kwargs):
        mongoclient = MongoClient(env('MONGO_URI'))
        db = mongoclient.get_database()
        videos_fs = gridfs.GridFS(db)
        mp3_fs = gridfs.GridFS(db)
        
        token, err = access.validate(self.request)

        if err:
            return response.Response({"error": err}, status=status.HTTP_400_BAD_REQUEST)
        else:
            file = self.request.FILES["file"]
        