# Manager/custom_filters.py
class NonEditedMessageFilter:
    def __call__(self, update):
        result = update.edited_message is None
        # Uncomment the following line for debugging:
        # print("NonEditedMessageFilter:", result)
        return result

    def check_update(self, update):
        return self.__call__(update)

non_edited_message_filter = NonEditedMessageFilter()

class EditedMessageFilter:
    def __call__(self, update):
        result = update.edited_message is not None
        # Uncomment the following line for debugging:
        # print("EditedMessageFilter:", result)
        return result

    def check_update(self, update):
        return self.__call__(update)

edited_message_filter = EditedMessageFilter()
