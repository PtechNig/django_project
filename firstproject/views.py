from bson import ObjectId  # Import ObjectId from the bson library
from rest_framework.request import Request 
from rest_framework.response import Response 
from rest_framework import status, generics, mixins
from .serializer import BlogSerializer
from django.conf import settings


class ContactListCreateView(generics.GenericAPIView, 
                            mixins.ListModelMixin, 
                            mixins.CreateModelMixin):
    serializer_class = BlogSerializer

    def get_queryset(self):
        # Return all contacts from MongoDB
        return list(settings.MONGO_DB.blogs.find())

    def get(self, request:Request,*args,**kwargs):
      return self.list(request, *args,**kwargs)

    def post(self, request: Request, *args, **kwargs):
        # Validate the incoming data using the serializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # If valid, insert the validated data into MongoDB
            settings.MONGO_DB.blogs.insert_one(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Implementing create() method to satisfy the CreateModelMixin requirement
    def create(self, request: Request, *args, **kwargs):
        # Call the post method directly
        return self.post(request, *args, **kwargs)

class ContactRetrieveUpdateDeleteView(generics.GenericAPIView,
                                      mixins.RetrieveModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin):
    serializer_class = BlogSerializer

    def get_object(self):
        obj_id = self.kwargs.get('pk')
        try:
            contact = settings.MONGO_DB.blogs.find_one({"_id": ObjectId(obj_id)})
            if contact is None:
                raise ValueError("Contact not found")  # Raise an error if no contact is found
            return contact
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging output
            return None
    
    def get(self, request: Request, *args, **kwargs):
        contact = self.get_object()
        if contact is None:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(contact)
        return Response(serializer.data)
    
    def put(self, request: Request, *args, **kwargs):
        contact = self.get_object()
        if contact is None:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                # Perform the update in MongoDB
                settings.MONGO_DB.blogs.update_one(
                    {"_id": ObjectId(kwargs.get('pk'))}, 
                    {"$set": serializer.validated_data}
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, *args, **kwargs):
        contact = self.get_object()
        if contact is None:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Perform the delete in MongoDB
            settings.MONGO_DB.blogs.delete_one({"_id": ObjectId(kwargs.get('pk'))})
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)