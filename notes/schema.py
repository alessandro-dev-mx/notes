# Standard library
from datetime import datetime as dt

# Third-party
import graphene
import pytz

# Local libs/modules
from note import schema


class Query(schema.Query, graphene.ObjectType):
    """Basic Query class to define and expose the "Notitas" data model
    """

    # Defining time field
    time = graphene.String(time_zone=graphene.String(
        default_value='America/Mexico_City'))

    # Resolver for retrieving the time of the requested time zone...
    def resolve_time(self, _, time_zone):
        """Calculates the time according to the provided time zone

        Args:
            _ (): [description]
            time_zone (str): name of a valid timezone

        Returns:
            str: formatted time of the specified time zone
        """

        # Define the IST time zone
        IST = pytz.timezone(time_zone)

        # Calculate the time and convert it into a string with a nice format...
        datetime_ist = dt.now(IST)
        formatted_time = datetime_ist.strftime('%Y:%m:%d %H:%M:%S %Z %z')

        return formatted_time


class MyMutations(schema.MyMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=MyMutations)
