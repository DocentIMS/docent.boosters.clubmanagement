

def after_edit_processor(context, event):
    if hasattr(context, 'after_edit_processor'):
        context.after_edit_processor()


def after_creation_processor(context, event):
    if hasattr(context, 'after_creation_processor'):
        context.after_creation_processor()


def after_transition_processor(context, event):
    if hasattr(context, 'after_transition_processor'):
        context.after_transition_processor()
