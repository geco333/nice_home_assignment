"""Page Object for the ParaBank update-profile page."""
from src.pages.base_page import BasePage


class UpdateProfilePage(BasePage):
    """Encapsulates interactions with the ParaBank profile update form.

    Allows updating customer contact information (name, address, phone).
    """

    PATH = "updateprofile.htm"

    # Form fields
    FIRST_NAME = "#customer\\.firstName"
    LAST_NAME = "#customer\\.lastName"
    ADDRESS = "#customer\\.address\\.street"
    CITY = "#customer\\.address\\.city"
    STATE = "#customer\\.address\\.state"
    ZIP_CODE = "#customer\\.address\\.zipCode"
    PHONE = "#customer\\.phoneNumber"
    UPDATE_BTN = "input[value='Update Profile']"

    # Result
    SUCCESS_HEADING = "#updateProfileResult h1"
    SUCCESS_MESSAGE = "#updateProfileResult p"

    # Validation errors
    ERROR_FIRST_NAME = "#firstName-error"
    ERROR_LAST_NAME = "#lastName-error"
    ERROR_ADDRESS = "#street-error"
    ERROR_CITY = "#city-error"
    ERROR_STATE = "#state-error"
    ERROR_ZIP_CODE = "#zipCode-error"

    def open(self) -> "UpdateProfilePage":
        """Navigate to the update-profile page.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        return self

    def get_first_name(self) -> str:
        """Return the current value of the first name field."""
        return self.page.input_value(self.FIRST_NAME)

    def get_last_name(self) -> str:
        """Return the current value of the last name field."""
        return self.page.input_value(self.LAST_NAME)

    def update_profile(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        address: str | None = None,
        city: str | None = None,
        state: str | None = None,
        zip_code: str | None = None,
        phone: str | None = None,
    ) -> None:
        """Clear and fill profile fields, then submit the form.

        Only non-None fields are overwritten; the rest keep their current values.

        :param first_name: New first name, or None to keep existing.
        :param last_name: New last name, or None to keep existing.
        :param address: New street address, or None to keep existing.
        :param city: New city, or None to keep existing.
        :param state: New state, or None to keep existing.
        :param zip_code: New zip code, or None to keep existing.
        :param phone: New phone number, or None to keep existing.
        """
        field_map = {
            self.FIRST_NAME: first_name,
            self.LAST_NAME: last_name,
            self.ADDRESS: address,
            self.CITY: city,
            self.STATE: state,
            self.ZIP_CODE: zip_code,
            self.PHONE: phone,
        }
        for selector, value in field_map.items():
            if value is not None:
                self.page.fill(selector, value)

        self.page.click(self.UPDATE_BTN)

    def get_success_heading(self) -> str:
        """Return the heading text after a successful update (e.g. 'Profile Updated')."""
        self.page.wait_for_selector(self.SUCCESS_HEADING, timeout=10000)
        return self.page.locator(self.SUCCESS_HEADING).inner_text()

    def get_success_message(self) -> str:
        """Return the success message paragraph text."""
        return self.page.locator(self.SUCCESS_MESSAGE).inner_text()

    def get_visible_errors(self) -> list[str]:
        """Return the text of all currently visible validation error messages.

        :returns: List of visible error message strings.
        """
        errors = self.page.locator("span.error:visible")
        return errors.all_inner_texts()
