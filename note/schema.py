# Third party libs
# from django.db import transaction
from graphene import AbstractType, Boolean, DateTime, Field, InputObjectType, Int, List, Mutation, String
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
    """Defines queries to fetch specific or all objects from DB
    """
    categories = List(CategoryType)
    category = Field(CategoryType, category_id=Int(), name=String())
    notes = List(NoteType)
    note = Field(NoteType, note_id=Int(), title=String())

    @staticmethod
    def resolve_notes(self, _):
        return Note.objects.all()

    @staticmethod
    def resolve_categories(self, _):
        return Category.objects.all()

    @staticmethod
    def resolve_category(self, _, category_id=None, name=None):
        if category_id is not None:
            return Category.objects.get(pk=category_id)
        if name is not None:
            return Category.objects.get(name=name)

    @staticmethod
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

    @staticmethod
    def mutate(cls, _, category_data=None):

        # Get input data
        name = category_data.get('name')
        description = category_data.get('description')

        # Check if the given name of the category already exists
        try:
            category = Category.objects.get(name=name)

            # Loop thorugh all the given data and update the records
            for key, val in category_data.items():
                if key != 'name':
                    setattr(category, key, val)

        # If we can't find an existing category then we'll need to create one...
        except Category.DoesNotExist:
            category = Category.objects.create(
                name=name, description=description)

        # Save all changes done
        category.save()

        return UpsertCategory(category)


class NoteInput(InputObjectType):
    title = String(required=True)
    note_id = Int()
    content = String()
    note_type = String()
    category = String()
    color = String()
    pinned = Boolean()
    reminder = DateTime()
    done = Boolean()


class AddNote(Mutation):
    """Add a whole new note to the system
    """
    note = Field(NoteType)

    class Arguments:
        note_data = NoteInput(required=True)

    @staticmethod
    def mutate(cls, _, note_data):
        # Get input data
        title = note_data.get('title')
        note_id = note_data.get('note_id')
        content = note_data.get('content')
        note_type = note_data.get('note_type')
        category = note_data.get('category')
        color = note_data.get('color')
        pinned = note_data.get('pinned')
        reminder = note_data.get('reminder')
        done = note_data.get('done')

        # If category is given get its PK to use it when creating the note
        if not category:
            category = Category.objects.get(pk=1)
        else:
            category = Category.objects.get(name=category)

        # When note type is not specified we can assume it is a normal note...
        if not note_type:
            note_type = 'Note'

        # We usually don't want to have a note pinned to the top of the board...
        if not pinned:
            pinned = False

        # Unless specified we should assume the note/task is not done...
        if not done:
            done = False

        note = Note(title=title, content=content, note_type=note_type,
                    category=category, color=color, pinned=pinned,
                    reminder=reminder, done=done)

        note.save()

        return AddNote(note)


class UpdateNote(Mutation):
    """Updates a note with the given fields
    """
    note = Field(NoteType)

    class Arguments:
        note_data = NoteInput(required=True)

    @staticmethod
    def mutate(cls, _, note_data):

        # Get input data
        title = note_data.get('title')
        note_id = note_data.get('note_id')
        content = note_data.get('content')
        note_type = note_data.get('note_type')
        category = note_data.get('category')
        color = note_data.get('color')
        pinned = note_data.get('pinned')
        reminder = note_data.get('reminder')
        done = note_data.get('done')

        # If category is given get its PK to use it when creating the note
        if not category:
            category = Category.objects.get(pk=1)
        else:
            category = Category.objects.get(name=category)
        note_data['category'] = category

        # When note type is not specified we can assume it is a normal note...
        if not note_type:
            note_type = 'Note'
            note_data['note_type'] = note_type

        # We usually don't want to have a note pinned to the top of the board...
        if not pinned:
            pinned = False
            note_data['pinned'] = pinned

        # Unless specified we should assume the note/task is not done...
        if not done:
            done = False
            note_data['done'] = done

        need_update = False

        # Check if the given Note already exists
        try:
            if note_id:
                note = Note.objects.get(pk=note_id)
                need_update = True
            else:
                raise Note.DoesNotExist
        except Note.DoesNotExist:
            print('Non-existing Note ID provided')
            raise

        # Loop thorugh all the given data and update the records
        for key, val in note_data.items():
            if key not in ('title'):
                setattr(note, key, val)

        # Save all changes done
        note.save()

        return UpdateNote(note)


class DeleteNote(Mutation):
    """Deletes notes based on the given ID (PK)
    """
    ok = Boolean()

    class Arguments:
        note_id = Int()

    @classmethod
    def mutate(cls, _, info, note_id):
        note = Note.objects.get(pk=note_id)
        note.delete()
        return cls(ok=True)


class DeleteCategory(Mutation):
    """Deletes categories based on the given ID (PK)
    """
    ok = Boolean()

    class Arguments:
        category_id = Int()

    @classmethod
    def mutate(cls, _, info, category_id):
        category = Category.objects.get(pk=category_id)
        category.delete()
        return cls(ok=True)


class MyMutation(AbstractType):
    """Main class containing all mutations required to create categories
    """
    # upsert_note = UpsertNote.Field()
    add_note = AddNote.Field()
    update_note = UpdateNote.Field()
    delete_note = DeleteNote.Field()
    upsert_category = UpsertCategory.Field()
    delete_category = DeleteCategory.Field()
