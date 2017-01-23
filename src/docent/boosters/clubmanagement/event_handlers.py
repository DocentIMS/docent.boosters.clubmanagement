

def after_edit_processor(context, event):
    if hasattr(context, 'after_edit_processor'):
        context.after_edit_processor()