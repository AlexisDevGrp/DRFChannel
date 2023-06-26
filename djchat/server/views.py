# This code defines a ServerListViewSet class that inherits from viewsets.ViewSet . It retrieves a list of servers based on different criteria specified in the request query parameters.
# The queryset attribute is set to retrieve all Server objects.
# The list method is called when the API is accessed. It first retrieves some query parameters from the request, such as "category", "qty", "by_user", "by_server_id", and "with_num_members".
# If the "by_user" parameter is set to "true", it checks if the user is authenticated. If the user is not authenticated, an AuthenticationFailed exception is raised.
# If the "category" parameter is set, it filters the queryset to retrieve only the servers that belong to that category.
# If the "by_user" parameter is set, it filters the queryset to retrieve only the servers that the user is a member of.
# If the "with_num_members" parameter is set to "true", it annotates the queryset with the number of members in each server.
# If the "qty" parameter is set, it limits the queryset to retrieve only the specified number of servers.
# If the "by_server_id" parameter is set, it filters the queryset to retrieve only the server with the specified ID. If the server doesn't exist, a ValidationError exception is raised.
# Finally, it serializes the queryset using the ServerSerializer and returns the serialized data as a HTTP response. The context parameter is passed to the serializer to include the number of members only when the "with_num_members" parameter is set.

from rest_framework import viewsets
from rest_framework.response import Response
from .models import Server                           # Importing the Server model
from .serializer import ServerSerializer             # Importing the ServerSerializer
from rest_framework.exceptions import ValidationError, AuthenticationFailed  # Importing some exception classes
from django.db.models import Count                   # Importing Count function from django.db.models
from .schema import server_list_docs
"""
    def list(self, request):
    Returns a list of servers based on the given query parameters.
    Args:
        request: The HTTP request object.
    Query Parameters:
        category (str): Filter servers by category name.
        qty (int): Limit the number of servers returned.
        by_user (bool): Filter servers by the current user.
        by_server_id (int): Filter servers by server ID.
        with_num_members (bool): Include the number of members in each server.
    Raises:
        AuthenticationFailed: If by_user is True and the user is not authenticated.
        ValidationError: If by_server_id is invalid or not found.
    Returns:
        
"""


class ServerListViewSet(viewsets.ViewSet):
    """
    A viewset that provides a list of servers based on different criteria.
    """

    queryset = Server.objects.all()     # Initializing the queryset to retrieve all Server objects
    
    @server_list_docs
    def list(self, request):
        """
        Method called when an HTTP GET request is made to the API.
        """

        category = request.query_params.get("category")     # Retrieve the "category" parameter from the query string
        qty = request.query_params.get("qty")               # Retrieve the "qty" parameter from the query string
        by_user = request.query_params.get("by_user") == "true"  # Retrieve the "by_user" parameter from the query string
        by_server_id = request.query_params.get("by_server_id")   # Retrieve the "by_server_id" parameter from the query string
        with_num_members = request.query_params.get("with_num_members") == "true"  # Retrieve the "with_num_members" parameter from the query string
      
        if category:
            self.queryset = self.queryset.filter(category__name=category)   # Filter the queryset by category name

        if by_user:
            if by_user and request.user.is_authenticated:
                user_id = request.user.id                             # Retrieve the user ID from the request
                self.queryset = self.queryset.filter(member=user_id)  # Filter the queryset by the user ID

        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))  # Annotate the queryset with the number of members in each server

        if qty:
            self.queryset = self.queryset[: int(qty)]      # Slice the queryset to retrieve only the specified number of servers

        if by_server_id:
            if not request.user.is_authenticated:
                raise AuthenticationFailed()
            try: 
                self.queryset = self.queryset.filter(id=by_server_id)  # Filter the queryset by server ID
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server: {by_server_id} is unknown.")  # Raise a ValidationError if the specified server doesn't exist
            except ValueError:
                raise ValidationError(detail=f"Sorry the system has found an error during the research (Error: {ValueError}) of the server with id: {by_server_id}")  # Raise a ValidationError if there is an error during the research

        serializer = ServerSerializer(self.queryset, many=True, context={"num_members": with_num_members})  # Serialize the queryset using the ServerSerializer
        return Response(serializer.data)     # Return a HTTP response with the serialized datae


