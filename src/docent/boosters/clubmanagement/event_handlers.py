

def after_edit_processor(context, event):
    if hasattr(context, 'after_edit_processor'):
        context.after_edit_processor()


def after_creation_processor(context, event):
    if hasattr(context, 'after_creation_processor'):
        context.after_creation_processor(context, event)

def after_object_added_processor(context, newParent):
    if hasattr(context, 'after_object_added_processor'):
        context.after_object_added_processor(context, newParent)