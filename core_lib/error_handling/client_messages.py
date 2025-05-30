from enum import Enum


class ClientMessage(Enum):
    FORM_FAILED_ASSERTION = ("form.failedAssertion", "Something went wrong while processing the form. Please contact support.")
    FORM_EMAIL_INVALID = ("form.emailInvalid", "The email address you entered is not valid.")
    FORM_DATE_INVALID = ("form.dateInvalid", "The selected date is not valid or incomplete.")

    @property
    def code(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]