# Third party libs
from graphene import AbstractType, Boolean, DateTime, Field, InputObjectType, Int, Mutation, String
from graphene_django import DjangoObjectType, DjangoListField
from graphql import GraphQLError

# Local modules
from .models import Category, Note


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class NoteType(DjangoObjectType):
    class Meta:
        model = Note


class Query(object):
    categories = DjangoListField(CategoryType)
    category = Field(CategoryType, category_id=Int(), name=String())
    notes = DjangoListField(NoteType)
    note = Field(NoteType, note_id=Int(), title=String())

    def resolve_category(self, _, category_id=None, name=None):
        if category_id is not None:
            return Category.objects.get(pk=category_id)
        if name is not None:
            return Category.objects.get(name=name)

    def resolve_note(self, _, note_id=None, title=None):
        if note_id is not None:
            return Note.objects.get(pk=note_id)
        if title is not None:
            return title.objects.get(title=title)


class CategoryInput(InputObjectType):
    name = String(required=True)
    description = String()


class UpsertCategory(Mutation):
    """Creates or updates a category depending on wether the name of the
    category is already registered or not...
    """
    category = Field(CategoryType)

    class Arguments:
        category_data = CategoryInput(required=True)

    def mutate(self, _, category_data=None):

        # Get input data
        name = category_data.get('name')
        description = category_data.get('description')

        # Check if the given name of the category already exists
        try:
            category = Category.objects.get(name=name)

            # Loop thorugh all the given data and update the records
            for key, val in category_data.items():
                setattr(category, key, val)

        # If we can't find an existing category then we'll need to create one...
        except Category.DoesNotExist:
            category = Category(name=name, description=description)

        # Save all changes done
        category.save()

        return UpsertCategory(category)


class NoteInput(InputObjectType):
    title = String(required=True)
    content = String()
    note_type = String()
    category = String()
    color = String()
    pinned = Boolean()
    reminder = DateTime()
    done = Boolean()


class UpsertNote(Mutation):
    """Creates or updates a note depending on wether the title of the
    note is already registered or not...
    """
    note = Field(NoteType)

    class Arguments:
        note_data = NoteInput(required=True)

    def mutate(self, _, note_data=None):

        # Get input data
        title = note_data.get('title')
        content = note_data.get('content')
        note_type = note_data.get('noteType')
        category = note_data.get('category')
        color = note_data.get('color')
        pinned = note_data.get('pinned')
        reminder = note_data.get('noteData')
        done = note_data.get('done')

        # If category is given get its PK to use it when creating the note
        if not category:
            category = 'General'
        category_res = Category.objects.get(name=category)
        if category_res:
            category = category_res
            note_data['category'] = category

        # When note type is not specified we can assume it is a normal note...
        if not note_type:
            note_type = 'Note'
            note_data['noteType'] = note_type

        # We usually don't want to have a note pinned to the top of the board...
        if not pinned:
            pinned = False
            note_data['pinned'] = pinned

        # Unless specified we should assume the note/task is not done...
        if not done:
            done = False
            note_data['done'] = done

        # Check if the given title of the Note already exists
        try:
            note = Note.objects.get(title=title)

            # Loop thorugh all the given data and update the records
            for key, val in note_data.items():
                setattr(note, key, val)

        # If we can't find an existing Note then we'll need to create one...
        except Note.DoesNotExist:
            note = Note(title=title, content=content, note_type=note_type,
                        category=category, color=color, pinned=pinned,
                        reminder=reminder, done=done)

        # Save all changes done
        note.save()

        return UpsertNote(note)


class MyMutation(AbstractType):
    """Main class containing all mutations required to create categories
    """
    upsert_category = UpsertCategory.Field()
    upsert_note = UpsertNote.Field()
